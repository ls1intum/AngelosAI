import { Routes } from '@angular/router';
import { ChatComponent } from './chat/chat.component';
import { LoginComponent } from './login/login.component';
import { AuthGuard } from './utils/auth.guard';
import { ImprintComponent } from './imprint/imprint.component';
import { PrivacyComponent } from './privacy/privacy.component';
import { RedirectComponent } from './utils/redirect.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'en', component: ChatComponent, canActivate: [AuthGuard], data: { language: 'en' } },
  { path: 'de', component: ChatComponent, canActivate: [AuthGuard], data: { language: 'de' } },
  { path: 'imprint', component: ImprintComponent, },
  { path: 'privacy', component: PrivacyComponent },
  { path: '', component: RedirectComponent },
  { path: '**', redirectTo: '' }
];