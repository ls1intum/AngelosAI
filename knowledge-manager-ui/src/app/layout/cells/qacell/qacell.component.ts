import { Component, Inject } from '@angular/core';

@Component({
  selector: 'app-qacell',
  standalone: true,
  imports: [],
  templateUrl: './qacell.component.html',
  styleUrl: './qacell.component.css'
})
export class QACellComponent {
  text: string;

  constructor(@Inject('cellValue') public value: string) {
    this.text = this.formatAnswer(value);
  }

  // Removes HTML elements from the answer
  private formatAnswer(answer: string): string {
    return answer.replace(/<[^>]+>/g, '').trim();
  }
}
