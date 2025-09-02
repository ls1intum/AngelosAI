import { Component, Inject, OnInit } from '@angular/core';
import { StudyProgramFilterButtonComponent } from "../../layout/buttons/study-program-filter/study-program-filter-button.component";
import { AddButtonComponent } from "../../layout/buttons/add-button/add-button.component";
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { StudyProgram } from '../../data/model/study-program.model';
import { SampleQuestion } from '../../data/model/sample-question.model';
import { TableColumn, MainTableComponent } from '../../layout/tables/main-table/main-table.component';
import { StudyProgramsCellComponent } from '../../layout/cells/study-programs-cell/study-programs-cell.component';
import { ActionsCellComponent } from '../../layout/cells/actions-cell/actions-cell.component';
import { StudyProgramService } from '../../services/study-program.service';
import { NgFor, NgIf } from '@angular/common';
import { DOCUMENT } from '@angular/common';
import { SampleQuestionDialogComponent } from '../../layout/dialogs/sample-question-dialog/sample-question-dialog.component';
import { BaseComponent } from '../base-template/base-template.component';
import { SampleQuestionService } from '../../services/sample-question.service';
import { Observable } from 'rxjs';
import { StudyProgramDTO } from '../../data/dto/study-program.dto';
import { SampleQuestionDTO } from '../../data/dto/sample-question.dto';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { SidebarFilterComponent } from '../../layout/sidebars/sidebar-filter/sidebar-filter.component';
import { MatPaginatorIntl, MatPaginatorModule } from '@angular/material/paginator';
import { CustomPaginatorIntl } from '../../layout/paginator/custom-paginator-intl.service';
import { SearchInputComponent } from '../../layout/inputs/search-input/search-input.component';
import { LoadingContainerComponent } from '../../layout/containers/loading-container/loading-container.component';

@Component({
  selector: 'app-samplequestions',
  standalone: true,
  imports: [
    SidebarFilterComponent,
    AddButtonComponent,
    MatDialogModule,
    MainTableComponent,
    NgIf,
    NgFor,
    MatSnackBarModule,
    MatPaginatorModule,
    SearchInputComponent,
    LoadingContainerComponent
  ],
  providers: [
    { provide: MatPaginatorIntl, useClass: CustomPaginatorIntl }  // Provide custom paginator text
  ],
  templateUrl: '../base-template/base-template.component.html',
  styleUrl: '../base-template/base-template.component.css'
})
export class SampleQuestionsComponent extends BaseComponent<SampleQuestion> {
  items: SampleQuestion[] = [];
  
  headerText = "Beispielfragen"
  addButtonText = "Beispielfrage hinzufügen"

  constructor(
    protected override dialog: MatDialog,
    protected override studyProgramService: StudyProgramService,
    protected override snackBar: MatSnackBar,
    @Inject(DOCUMENT) protected override document: Document,
    private sampleQuestionService: SampleQuestionService
  ) {
    super(dialog, studyProgramService, snackBar, document);
  }
  
  override fetchData(): void {
    this.sampleQuestionService.getAllSampleQuestions().subscribe({
      next: (sampleQuestions: SampleQuestion[]) => {
        this.items = sampleQuestions;
        this.displayedItems = [...sampleQuestions];
        this.loading = false;
      },
      error: (error: any) => {
        this.handleError("Fehler beim Laden der Websites. Bitte laden Sie die Seite erneut.");
        this.loading = false;
      }
    });
  }

  columns: TableColumn<SampleQuestion>[] = [
    {
      key: 'topic',
      header: 'Thema',
      value: (sq: SampleQuestion) => sq.topic,
      primary: true,
      sort: true,
      sortAccessor: (sq: SampleQuestion) => sq.topic?.toLowerCase() ?? ''
    },
    {
      key: 'question',
      header: 'Frage',
      value: (sq: SampleQuestion) => sq.question,
    },
    {
      key: 'answer',
      header: 'Antwort',
      value: (sq: SampleQuestion) => sq.answer,
    },
    {
      key: 'studyPrograms',
      header: 'Studiengänge',
      cellComponent: StudyProgramsCellComponent,
    },
    {
      key: 'actions',
      header: '',
      cellComponent: ActionsCellComponent,
    },
  ];

  override getDialogConfig(item?: SampleQuestion | undefined): { data: any; component: any; } {
    return {
      data: {
        ...item,
        availableStudyPrograms: this.availableStudyPrograms,
        selectedProgram: this.selectedProgram,
        studyPrograms: item?.studyPrograms || [],
      },
      component: SampleQuestionDialogComponent
    }
  }
  override getDeleteDialogText(item: SampleQuestion): { title: string; message: string; } {
    return {
      title: 'Beispielfrage löschen',
      message: `Sind Sie sicher, dass Sie die Beispielfrage zu dem Thema "${item.topic}" löschen wollen?`
    }
  }

  override deleteData(id: string): Observable<void> {
    return this.sampleQuestionService.deleteSampleQuestion(id);
  }

  override editItem(item: SampleQuestion): Observable<SampleQuestion> {
    return this.sampleQuestionService.editSampleQuestion(item.id, this.createDTO(item))
  }

  onEdit(sampleQuestion: SampleQuestion): void {
    this.openAddOrEditDialog(sampleQuestion);
  }

  private createDTO(data: SampleQuestion): SampleQuestionDTO {
    const dto: SampleQuestionDTO = {
      id: data.id,
      topic: data.topic,
      question: data.question,
      answer: data.answer,
      studyPrograms: data.studyPrograms.map(this.toSPDTO),
    }
    return dto;
  }

  private toSPDTO(sp: StudyProgram): StudyProgramDTO {
    return {
      id: sp.id,
      name: sp.name,
    };
  }

  protected matchSearch(item: SampleQuestion, searchTerm: string): boolean {
    if (! searchTerm || searchTerm == "") {
      return true;
    }
    const lowerTerm = searchTerm.toLowerCase();
    return (
      item.question.toLowerCase().includes(lowerTerm) ||
      item.answer.toLowerCase().includes(lowerTerm) ||
      item.topic.toLowerCase().includes(lowerTerm)
    );
  }
}
