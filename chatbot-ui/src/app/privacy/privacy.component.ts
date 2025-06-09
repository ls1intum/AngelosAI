import { Component } from '@angular/core';
import { HeaderComponent } from '../utils/header/header.component';

@Component({
  selector: 'app-privacy',
  standalone: true,
  imports: [
    HeaderComponent
  ],
  templateUrl: './privacy.component.html',
  styleUrl: './privacy.component.scss'
})
export class PrivacyComponent {

}
