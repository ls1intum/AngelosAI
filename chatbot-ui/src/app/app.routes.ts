import { Routes } from '@angular/router';
import { ChatComponent } from './chat/chat.component';
import { LoginComponent } from './login/login.component';
import { AuthGuard } from './utils/auth.guard';
import { ImprintComponent } from './imprint/imprint.component';
import { PrivacyComponent } from './privacy/privacy.component';
import { RedirectComponent } from './utils/redirect.component';
import { PrivacyEnComponent } from './privacy_en/privacy.component';
import { ImprintEnComponent } from './imprint_en/imprint.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'en', component: ChatComponent, canActivate: [AuthGuard], data: { language: 'en' } },
  { path: 'de', component: ChatComponent, canActivate: [AuthGuard], data: { language: 'de' } },
  { path: 'imprint', component: ImprintEnComponent, },
  { path: 'impressum', component: ImprintComponent, },
  { path: 'datenschutz', component: PrivacyComponent },
  { path: 'privacy', component: PrivacyEnComponent },
  { path: '', component: RedirectComponent },
  { path: '**', redirectTo: '' }
];