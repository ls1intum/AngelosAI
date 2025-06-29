import { Component, OnInit, Inject } from '@angular/core';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { DOCUMENT, NgClass, NgIf } from '@angular/common';
import { UserService } from '../../services/user.service';
import { StudyProgramService } from '../../services/study-program.service';
import { User } from '../../data/model/user.model';
import { StudyProgram } from '../../data/model/study-program.model';
import { TableColumn, MainTableComponent } from '../../layout/tables/main-table/main-table.component';
import { ActionsCellComponent } from '../../layout/cells/actions-cell/actions-cell.component';
import { ConfirmDialogComponent } from '../../layout/dialogs/confirm-dialog/confirm-dialog.component';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { forkJoin, mergeMap } from 'rxjs';
import { AddButtonComponent } from "../../layout/buttons/add-button/add-button.component";
import { StudyProgramDialogComponent } from './study-program-dialog/study-program-dialog.component';
import { StudyProgramDTO } from '../../data/dto/study-program.dto';
import { MailService, MailStatus } from '../../services/mail.service';
import { MailDialogComponent } from '../../layout/dialogs/mail-dialog/mail-dialog.component';
import { AuthenticationService } from '../../services/authentication.service';
import { Organisation } from '../../data/model/organisation.model';
import { OrganisationComponent } from "./organisation/organisation.component";
import { MatPaginatorIntl, MatPaginatorModule } from '@angular/material/paginator';
import { CustomPaginatorIntl } from '../../layout/paginator/custom-paginator-intl.service';
import { UserDetailsDTO } from '../../data/dto/user-details.dto';
import { StudyProgramAdmin } from '../../data/model/study-program-admin.model';
import { StatusButtonComponent } from '@app/layout/buttons/status-button/status-button.component';
import { MatIconModule } from '@angular/material/icon';
import { OrganisationService } from '@app/services/organisation.service';
import { StatusCardComponent } from '@app/layout/cards/status-card/status-card.component';


@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [
    MatDialogModule,
    MatIconModule,
    MainTableComponent,
    MatSnackBarModule,
    NgIf,
    AddButtonComponent,
    OrganisationComponent,
    MatPaginatorModule,
    StatusCardComponent
  ],
  providers: [
    { provide: MatPaginatorIntl, useClass: CustomPaginatorIntl }
  ],
  templateUrl: './admin.component.html',
  styleUrl: './admin.component.css'
})
export class AdminComponent implements OnInit {

  public MailStatus = MailStatus;
  protected userIsSystemAdmin: boolean = false;
  protected chatbotActive: boolean = false;

  currentUser: UserDetailsDTO | null = null;

  mailStatus: MailStatus | null = null;
  mailCredentials: string | null = null;
  organisationUrl: string | null = null;
  statusText: string = "";

  users: User[] = [];

  protected organisations: Organisation[] = [];

  studyPrograms: StudyProgramAdmin[] = [];

  // Define user columns
  userColumns: TableColumn<User>[] = [
    {
      key: 'mail',
      header: 'E-Mail',
      value: (user: User) => user.mail,
      primary: true
    },
    {
      key: 'isApproved',
      header: 'Status',
      value: (user: User) => {
        if (!user.isApproved) {
          return "Unbestätigt";
        } else if (user.isApproved && !user.isAdmin) {
          return "Teammitglied";
        } else {
          return "Administrator";
        }
      },
      primary: false
    },
    {
      key: 'actions',
      header: '',
      cellComponent: ActionsCellComponent,
    }
  ];

  // Define study program columns
  studyProgramColumns: TableColumn<StudyProgramAdmin>[] = [
    {
      key: 'name',
      header: 'Name',
      value: (sp: StudyProgramAdmin) => sp.name,
      primary: true
    },
    {
      key: 'actions',
      header: '',
      cellComponent: ActionsCellComponent,
    },
  ];


  constructor(
    protected dialog: MatDialog,
    protected studyProgramService: StudyProgramService,
    protected authService: AuthenticationService,
    protected userService: UserService,
    protected snackBar: MatSnackBar,
    protected mailService: MailService,
    protected organisationService: OrganisationService,
    @Inject(DOCUMENT) protected document: Document
  ) { }

  ngOnInit(): void {
    this.userService.getCurrentUser().pipe(
      mergeMap((userDTO) => {
        this.currentUser = userDTO;
        this.userIsSystemAdmin = this.currentUser.isSystemAdmin;
        this.chatbotActive = this.currentUser.organisationActive;
        this.organisationUrl = this.currentUser.organisationUrl? this.currentUser.organisationUrl! : null;

        return forkJoin({
          programs: this.studyProgramService.fetchStudyPrograms(),
          users: this.userService.getAllUsers(this.currentUser ? this.currentUser.isAdmin : false, this.userIsSystemAdmin)
        });
      }),
      mergeMap(({ programs, users }) => {
        this.studyPrograms = programs.map(sp => this.mapToAdminStudyProgram(sp));
        this.users = users;
        return this.authService.getAccessToken();
      }),
      mergeMap(token => {
        if (!token) {
          throw new Error("No access token available");
        }
        return this.mailService.getMailCredentials(token);
      }))
      .subscribe({
        next: (mailCredentialsResponse) => {
          this.mailCredentials = mailCredentialsResponse.mailAccount;
          this.mailService.mailStatus$.subscribe((status) => {
            this.mailStatus = status;
            this.statusText = this.getStatusText(status);
          });
        },
        error: (err) => {
          console.error('Error in data fetching sequence:', err);
          this.handleError('Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.');
        },
      });
  }

  onApprove(user: User) {
    // Call a userService method to approve user
    const title = "Bestätigen"
    // Resourcen verwalten
    const message = "Wollen Sie dieses Teammitglied bestätigen?"

    this.dialog.open(ConfirmDialogComponent, {
      data: { title, message },
    }).afterClosed().subscribe((confirmed: boolean) => {
      if (confirmed) {
        this.userService.approveUser(user.id).subscribe({
          next: (updatedUser: User) => {
            this.updateUserInArray(updatedUser);
            this.handleSuccess('Das Teammitglied wurde erfolgreich bestätigt.');
          },
          error: (error) => {
            console.error("Error during approve user", error)
            this.handleError("Es ist ein Fehler aufgetreten. Der Benutzer konnte nicht als Teammitglied hinzugefügt werden. Bitte versuchen Sie es später erneut.")
          }
        });
      }
    });
    // ...
  }

  onSetAdmin(user: User) {
    const title = "Bestätigen"
    // Erklärung?
    const message = "Wollen Sie dieses Teammitglied zum Administrator für Ihre Organisation machen?"

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: { title, message },
    });

    dialogRef.afterClosed().subscribe((confirmed: boolean) => {
      if (confirmed) {
        this.userService.setUserToAdmin(user.id).subscribe({
          next: (updatedUser: User) => {
            this.updateUserInArray(updatedUser);
            this.handleSuccess('Das Teammitglied wurde erfolgreich zum Administrator gemacht.');
          },
          error: (error) => {
            console.error("Error during set admin", error)
            this.handleError("Fehler beim Festlegen des Benutzers als Administrator. Bitte versuchen Sie es später erneut.");
          }
        });
      }
    });
  }

  // Delete study program
  onDelete(studyProgram: StudyProgramAdmin) {
    const title = "Studiengang löschen"
    // Erklärung?
    const message = `Sind Sie sicher, dass sie den Studiengang „${studyProgram.name}“ löschen möchten? Alle damit verbundenen Ressourcen werden ebenfalls gelöscht.`

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: { title, message },
    });

    dialogRef.afterClosed().subscribe((confirmed: boolean) => {
      if (confirmed) {
        this.studyProgramService.deleteStudyProgram(studyProgram.id).subscribe({
          next: () => {
            this.refreshStudyPrograms();
            this.handleSuccess('Der Studiengang wurde erfolgreich gelöscht..');
          },
          error: (error) => {
            console.error("Error during deletion of study program", error)
            this.handleError("Der Studiengang konnte nicht gelöscht werden. Bitte versuchen Sie es später erneut.");
          }
        });
      }
    });
  }

  // Remove user from organisation
  onRemove(user: User) {
    const title = "Bestätigen"
    // Erklärung?
    const message = "Wollen Sie dieses Teammitglied aus Ihrer Organisation entfernen?"

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: { title, message },
    });

    dialogRef.afterClosed().subscribe((confirmed: boolean) => {
      if (confirmed) {
        this.userService.removeUser(user.id).subscribe({
          next: (updatedUser: User) => {
            this.updateUserInArray(updatedUser);
            this.handleSuccess('Das Teammitglied wurde erfolgreich entfernt.');
          },
          error: (error) => {
            console.error("Error during remove user", error)
            this.handleError("Fehler beim Entfernen des Benutzers. Bitte versuchen Sie es später erneut.");
          }
        });
      }
    });
  }

  addStudyProgram() {
    const accessToken = this.authService.getAccessToken();
    const dialogRef = this.dialog.open(StudyProgramDialogComponent, {
      data: { name: '', token: accessToken }
    });

    dialogRef.afterClosed().subscribe((result: StudyProgramDTO) => {
      if (result !== null && result !== undefined) {
        this.refreshStudyPrograms();
        this.handleSuccess("Studiengang erfolgreich hinzugefügt.");
      } else if (result === null) {
        this.handleError('Studiengang konnte nicht hinzugefügt werden.');
      }
    });
  }

  configureMail(): void {
    this.dialog.open(MailDialogComponent, {
      data: {
        mailAccount: this.mailCredentials || '',
        password: '',
        confirmPassword: ''
      },
      width: '600px'
    })
      .afterClosed().subscribe((result: boolean | null) => {
        if (result == false) {
          this.mailService.setMailStatus(MailStatus.INACTIVE);
          this.handleError("Fehler bei der Konfiguration des E-Mail-Accounts.");
        } else if (typeof result === 'string') {
          this.mailService.setMailStatus(MailStatus.ACTIVE);
          this.mailCredentials = result;
          this.handleSuccess("E-Mail-Account erfolgreich konfiguriert.");
        }
      });
  }

  changeChatbotStatus() : void {
    const title = this.chatbotActive ? 'Chatbot pausieren?' : 'Chatbot aktivieren?';
    // Erklärung?
    const message = this.chatbotActive
      ? 'Möchten Sie die automatische Antwortgenerierung wirklich ausschalten? Chatnachrichten werden nicht mehr beantwortet.'
      : 'Möchten Sie die automatische Antwortgenerierung wieder einschalten? Chatbot-Anfragen werden wieder automatisch beantwortet.';

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: { title, message },
    });

    dialogRef.afterClosed().subscribe((confirmed: boolean) => {
      if (confirmed) {
        this.organisationService.setResponseActive(!this.chatbotActive).subscribe({
          next: (org: any) => {
            this.chatbotActive = ! this.chatbotActive;
            this.handleSuccess(
              this.chatbotActive
                ? 'Automatische Antworten wurden erfolgreich aktiviert. Der Chatbot ist jetzt aktiv.'
                : 'Automatische Antworten wurden erfolgreich pausiert. Der Chatbot ist deaktiviert.'
            );
          },
          error: (error) => {
            console.error('Error during status change', error);
            this.handleError('Fehler beim Ändern des Antwortstatus. Bitte versuchen Sie es später erneut.');
          }
        });
      }
    });
  }

  changeMailStatus() : void {
    const mailActive = this.mailStatus === MailStatus.ACTIVE;
    const title = mailActive ? 'Mail-Antworten pausieren?' : 'Mail-Antworten aktivieren?';
    // Erklärung?
    const message = mailActive
      ? 'Möchten Sie die automatische Antwortgenerierung wirklich ausschalten? Mails werden nicht mehr automatisch beantwortet.'
      : 'Möchten Sie die automatische Antwortgenerierung wieder einschalten? Mail-Anfragen werden wieder automatisch beantwortet.';

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: { title, message },
    });

    dialogRef.afterClosed().subscribe((confirmed: boolean) => {
      if (confirmed) {
        this.organisationService.setMailActive(mailActive).subscribe({
          next: () => {
            this.mailStatus = mailActive ? MailStatus.INACTIVE : MailStatus.ACTIVE
            this.handleSuccess(
              this.mailStatus === MailStatus.ACTIVE
                ? 'Automatische Antworten wurden erfolgreich aktiviert. Die Mail-Pipeline ist jetzt aktiv.'
                : 'Automatische Antworten wurden erfolgreich pausiert. Mails werden nicht mehr automatisch beantwortet.'
            );
          },
          error: (error) => {
            console.error('Error during status change', error);
            this.handleError('Fehler beim Ändern des Antwortstatus. Bitte versuchen Sie es später erneut.');
          }
        });
      }
    });
  }

  onDeleteAccount() {
    const title = "Account unwiderruflich löschen";
    const message = "Sind Sie sicher, dass Sie Ihren Account und alle zugehörigen Daten dauerhaft löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.";
  
    this.dialog.open(ConfirmDialogComponent, {
      data: { title, message }
    }).afterClosed().subscribe((confirmed: boolean) => {
      if (confirmed) {
        this.userService.deleteCurrentUser().subscribe({
          next: () => {
            this.handleSuccess('Account erfolgreich gelöscht. Sie werden abgemeldet.');
            this.authService.logout();
          },
          error: (err) => {
            this.handleError('Account konnte nicht gelöscht werden. Bitte versuchen Sie es erneut.');
            console.error('Delete account error:', err);
          }
        });
      }
    });
  }

  private updateUserInArray(updatedUser: User): void {
    const index = this.users.findIndex(user => user.id === updatedUser.id);
    if (index !== -1) {
      this.users[index] = updatedUser;
      this.users = [...this.users];
    }
  }

  private handleError(errorMessage: string): void {
    this.snackBar.open(errorMessage, 'Schließen', {
      duration: 4000,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: ['error-snack-bar']
    });
  }

  private handleSuccess(successMessage: string): void {
    this.snackBar.open(successMessage, 'Schließen', {
      duration: 4000,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: ['success-snack-bar'],
    });
  }

  private getStatusText(status: MailStatus | null): string {
    if (status === MailStatus.ACTIVE) {
      return "Der konfigurierte E-Mail-Account für die automatische Beantwortung von E-Mails ist aktiv.";
    } else if (status === MailStatus.INACTIVE) {
      return "Der konfigurierte E-Mail-Account ist inaktiv. Bitte geben Sie die Zugangsdaten erneut ein, um die Pipeline zu reaktivieren.";
    } else {
      return "Es ist ein Fehler beim Abrufen des E-Mail-Account-Status aufgetreten. Bitte versuchen Sie es später erneut oder geben Sie die Zugangsdaten erneut ein, um die Pipeline zu reaktivieren.";
    }
  }

  private refreshStudyPrograms() {
    this.studyProgramService.fetchStudyPrograms().subscribe({
      next: (programs) => {
        this.studyPrograms = (programs as StudyProgram[]).map(
          sp => this.mapToAdminStudyProgram(sp)
        ).sort((a, b) => {
          const nameA = a.name.toLowerCase();
          const nameB = b.name.toLowerCase();

          if (nameA < nameB) return -1;
          if (nameA > nameB) return 1;
          return 0;
        });
      },
      error: (err) => {
        console.error("Error fetching study programs", err);
        this.handleError("Studiengänge konnten nicht neu geladen werden.");
      }
    });
  }

  private mapToAdminStudyProgram(sp: StudyProgram): StudyProgramAdmin {
    return {
      id: sp.id,
      name: sp.name,
      actions: this.currentUser && this.currentUser.isAdmin ? ["delete"] : []
    }
  }
}