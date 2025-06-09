// redirect.component.ts
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-redirect',
  template: ''
})
export class RedirectComponent implements OnInit {
  constructor(private router: Router) {}

  ngOnInit(): void {
    if (environment.loginRequired) {
      this.router.navigate(['/login']);
    } else {
      this.router.navigate(['/en']);
    }
  }
}