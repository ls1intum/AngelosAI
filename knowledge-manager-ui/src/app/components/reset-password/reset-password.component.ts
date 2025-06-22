import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { CustomDotLoaderComponent } from '@app/layout/containers/custom-dot-loader/custom-dot-loader.component';
import { AuthenticationService } from '@app/services/authentication.service';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    CustomDotLoaderComponent
  ],
  templateUrl: './reset-password.component.html',
  styleUrl: './reset-password.component.css'
})
export class ResetPasswordComponent {
  password: string = '';
  confirmPassword: string = '';
  successMessage: string = '';
  errorMessage: string = '';
  resetToken: string | null = null;
  loading = false;
  token = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthenticationService
  ) {
    this.token = this.route.snapshot.queryParamMap.get('token') || '';
  }


  onSubmit() {
    this.errorMessage = '';
    this.successMessage = '';
    if (this.password !== this.confirmPassword) {
      this.errorMessage = 'Passwörter stimmen nicht überein.';
      return;
    }
    this.loading = true;
    this.authService.resetPassword(this.token, this.password).subscribe({
      next: () => {
        this.successMessage = 'Passwort erfolgreich geändert.';
        this.loading = false;
        setTimeout(() => this.router.navigate(['/login']), 2000);
      },
      error: (err) => {
        this.errorMessage = err?.error?.message || 'Fehler beim Zurücksetzen des Passworts.';
        this.loading = false;
      }
    });
  }
}
