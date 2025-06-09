import { CommonModule } from '@angular/common';
import { Component, Inject } from '@angular/core';

@Component({
  selector: 'app-feedback-cell',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './feedback-cell.component.html',
  styleUrl: './feedback-cell.component.css'
})
export class FeedbackCellComponent {
  text: string;

  constructor(@Inject('cellValue') public value: string) {
    this.text = this.formatAnswer(value);
  }

  // Removes HTML elements from the answer
  private formatAnswer(answer: string): string {
    return answer.replace(/<[^>]+>/g, '').trim();
  }
}
