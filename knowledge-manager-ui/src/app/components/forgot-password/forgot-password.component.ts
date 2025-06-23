import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { CustomDotLoaderComponent } from '@app/layout/containers/custom-dot-loader/custom-dot-loader.component';
import { AuthenticationService } from '@app/services/authentication.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    CustomDotLoaderComponent
  ],
  templateUrl: './forgot-password.component.html',
  styleUrl: './forgot-password.component.css'
})
export class ForgotPasswordComponent {
  email: string = '';
  successMessage: string = '';
  errorMessage: string = '';
  loading = false;

  constructor(
    private authService: AuthenticationService,
  ) { }

  onSubmit() {
    this.successMessage = '';
    this.errorMessage = '';
    this.loading = true;

    this.authService.forgotPassword(this.email).subscribe({
      next: () => {
        this.successMessage = 'Falls diese Mail existiert, wurde ein Reset-Link gesendet.';
        this.loading = false;
      },
      error: (err) => {
        this.errorMessage = err?.error?.message || 'Fehler beim Senden der E-Mail.';
        this.loading = false;
      }
    });
  }
}
