import { NgClass, NgIf } from '@angular/common';
import { Component, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';

type Status = 'active' | 'inactive' | 'error';

@Component({
  selector: 'app-status-card',
  standalone: true,
  imports: [
    NgIf,
    NgClass,
    MatIconModule
  ],
  templateUrl: './status-card.component.html',
  styleUrl: './status-card.component.css'
})
export class StatusCardComponent {
  @Input() title = '';
  @Input() leadingIcon = '';
  @Input() trailingIcon = '';
  @Input() status: Status = 'inactive';
  @Input() subtitle = '';

  /** Callback executed when the card is clicked */
  @Input() onEdit: () => void = () => {};

  /** CSS class for the coloured border */
  get borderClass(): string {
    switch (this.status) {
      case 'active':
        return 'status-active';
      case 'error':
        return 'status-error';
      default:
        return 'status-inactive';
    }
  }

  handleClick(): void {
    // Fire callback if supplied
    if (this.onEdit) {
      this.onEdit();
    }
  }

  getStatusText(status: Status): string {
    if (status === "inactive") {
      return "Inaktiv";
    } else if (status === "active") {
      return "Aktiv"
    } else {
      return "Fehler";
    }
  }
}