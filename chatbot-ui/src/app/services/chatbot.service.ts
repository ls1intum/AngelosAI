import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ChatMessage } from '../chat/chat.component';
import { Observable, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ChatbotService {
  private url = environment.angelosUrl;
  private orgId: number = environment.organisation;
  private filterByOrg: boolean = environment.filterByOrg;

  constructor(private http: HttpClient, private authService: AuthService) { }

  sendBotRequest(token: string | null, chatHistory: ChatMessage[], study_program: string): Observable<any> {
    let headers = new HttpHeaders().set('x-api-key', environment.angelosAppApiKey);
    
    if (token && environment.loginRequired) {
      headers = headers.set('ChatAuth', `Bearer ${token}`);
    }

    return this.http.post(
      `${this.url}/chat/send?filterByOrg=${this.filterByOrg}`,
      {
        messages: chatHistory,
        study_program: study_program,
        orgId: this.orgId
      },
      { headers }
    );
  }

  getBotResponse(chatHistory: ChatMessage[], study_program: string): Observable<any> {
    const token = this.authService.getToken();
    if (token || ! environment.loginRequired) {
      return this.sendBotRequest(token, chatHistory, study_program);
    } else {
      return throwError(() => new Error('TokenMissing'));
    }
  }
}
