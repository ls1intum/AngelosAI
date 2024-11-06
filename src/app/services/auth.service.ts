import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import * as CryptoJS from 'crypto-js';

export interface AuthResponse {
  access_token: string;
  token_type: string;
}
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private isAuthenticated = new BehaviorSubject<boolean>(this.getToken() !== null);

  constructor(private http: HttpClient) { }

  login(username: string, password: string): Observable<AuthResponse> {
    const headers = new HttpHeaders().set('x-api-key', environment.angelosAppApiKey);
    const body = { username: username, password: password };
    return this.http.post<AuthResponse>(environment.angelosToken, body, { headers }).pipe(
      tap((response: AuthResponse) => {
        sessionStorage.setItem('access_token', response.access_token);
        this.isAuthenticated.next(true);
      })
    );
  }

  logout(): void {
    sessionStorage.removeItem('access_token');
    this.isAuthenticated.next(false);
  }

  getToken(): string | null {
    return sessionStorage.getItem('access_token');
  }

  isLoggedIn(): Observable<boolean> {
    return this.isAuthenticated.asObservable();
  }
}
