import { Component } from '@angular/core';
import { HeaderComponent } from '../utils/header/header.component';

@Component({
  selector: 'app-imprint',
  standalone: true,
  imports: [
    HeaderComponent
  ],
  templateUrl: './imprint.component.html',
  styleUrl: './imprint.component.scss'
})
export class ImprintComponent {

}
