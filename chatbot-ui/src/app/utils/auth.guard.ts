import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { Observable, of } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { environment } from '../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class AuthGuard implements CanActivate {
    constructor(private authService: AuthService, private router: Router) { }

    canActivate(): Observable<boolean> {
        if (!environment.loginRequired) {
            return of(true);
          }
      
          // Otherwise, check auth state
          return this.authService.isLoggedIn().pipe(
            tap(isLoggedIn => {
              if (!isLoggedIn) {
                this.router.navigate(['/login']);
              }
            })
          );
    }
}

