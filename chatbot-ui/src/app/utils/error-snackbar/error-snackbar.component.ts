import { NgIf } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-error-snackbar',
  standalone: true,
  imports: [NgIf],
  templateUrl: './error-snackbar.component.html',
  styleUrl: './error-snackbar.component.scss'
})
export class ErrorSnackbarComponent {
  message: string = '';
  isVisible: boolean = false;

  showError(message: string, duration: number = 5000): void {
    this.message = message;
    this.isVisible = true;

    setTimeout(() => {
      this.isVisible = false;
    }, duration);
  }

  dismiss(): void {
    this.isVisible = false;
  }
}
