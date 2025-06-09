import { NgIf } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-success-snackbar',
  standalone: true,
  imports: [NgIf],
  templateUrl: './success-snackbar.component.html',
  styleUrl: './success-snackbar.component.scss'
})
export class SuccessSnackbarComponent {
  message: string = '';
  isVisible: boolean = false;

  showMessage(message: string, duration: number = 5000): void {
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
