import { Routes } from '@angular/router';
import { ChatComponent } from './chat/chat.component';
import { LoginComponent } from './login/login.component';
import { AuthGuard } from './utils/auth.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'en', component: ChatComponent, canActivate: [AuthGuard], data: { language: 'en' } },
  { path: 'de', component: ChatComponent, canActivate: [AuthGuard], data: { language: 'de' } },
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: '**', redirectTo: 'login', pathMatch: 'full' }
];