// register.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';

import { OrganisationService } from '../../services/organisation.service';
import { OrganisationDTO } from '../../data/dto/organisation.dto';
import { AuthenticationService } from '../../services/authentication.service'; // Import the service and UserDTO
import { UserDTO } from '../../data/dto/user.dto';
import { finalize } from 'rxjs';
import { CustomDotLoaderComponent } from '@app/layout/containers/custom-dot-loader/custom-dot-loader.component';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MatIconModule, CustomDotLoaderComponent],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {
  email: string = '';
  password: string = '';
  confirmPassword: string = '';

  selectedOrganisation: OrganisationDTO | null = null;
  organisations: OrganisationDTO[] = [];

  dropdownOpen = false;

  successMessage: string | null = null;
  errorMessage: string | null = null;
  protected loading: boolean = false;

  constructor(
    private organisationService: OrganisationService,
    private authService: AuthenticationService // Use the auth service
  ) { }

  ngOnInit() {
    this.organisationService.getOrganisations()
      .subscribe({
        next: (orgs) => {
          this.organisations = orgs;
        },
        error: (err) => {
          console.error('Failed to load organisations', err);
        }
      });
  }

  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  selectOrganisation(org: OrganisationDTO) {
    this.selectedOrganisation = org;
    this.dropdownOpen = false;
  }

  clearSelection() {
    this.selectedOrganisation = null;
    this.dropdownOpen = false;
  }

  onRegister() {
    this.successMessage = null;
    this.errorMessage = null;
    if (this.loading) {
      return;
    }
    this.loading = true;
    if (this.password !== this.confirmPassword) {
      this.errorMessage = 'Die Passwörter stimmen nicht überein.';
      return;
    }

    if (!this.selectedOrganisation) {
      this.errorMessage = 'Bitte wählen Sie eine Organisation aus.';
      return;
    }

    // Call the authService.register method instead of http.post
    this.authService.register(this.email, this.password, this.selectedOrganisation.id).pipe(
      finalize(() => this.loading = false),
    )
      .subscribe({
        next: (user: UserDTO) => {
          this.successMessage = `Eine E-Mail wurde an ${user.mail} gesendet. Bitte bestätigen Sie Ihr Konto.`;
          this.errorMessage = null;
          // Clear the form
          this.email = '';
          this.password = '';
          this.confirmPassword = '';
          this.selectedOrganisation = null;
        },
        error: (err) => {
          console.error('Registration failed', err);
          this.errorMessage = 'Registrierung fehlgeschlagen. Bitte überprüfen Sie Ihre Eingaben oder versuchen Sie es später erneut.';
          this.successMessage = null;
        }
      });
  }
}