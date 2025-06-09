import { CommonModule } from '@angular/common';
import { Component, Inject, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-feedback',
  standalone: true,
  imports: [
    MatIconModule,
    CommonModule
  ],
  templateUrl: './feedback.component.html',
  styleUrl: './feedback.component.css'
})
export class FeedbackComponent {
  type: string;

  constructor(
    @Inject('cellValue') public value: any,
  ) {
    this.type = value;
  }

  /** Determine CSS class / icon based on type */
  get isPositive(): boolean {
    return this.type?.toLowerCase() === 'positive';
  }
  get isNegative(): boolean {
    return this.type?.toLowerCase() === 'negative';
  }
  get text(): string {
    return this.type === 'positive' ? "Positiv" : this.type === "negative"? "Negativ" : "Unbekannt";
  }

  /** Pick the right Material icon name */
  get iconName(): string {
    if (this.isPositive)   return 'thumb_up';
    if (this.isNegative)   return 'thumb_down';
    return 'help_outline';
  }

  /** Pick the right CSS class for color */
  get badgeClass(): 'positive' | 'negative' | 'unknown' {
    if (this.isPositive)   return 'positive';
    if (this.isNegative)   return 'negative';
    return 'unknown';
  }
}
