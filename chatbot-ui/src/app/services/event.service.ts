import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class EventService {
  private url = environment.angelosUrl;
  private orgId: number = environment.organisation;

  constructor(private http: HttpClient) { }

  logEvent(eventType: string, metadata: string): Observable<any> {
    const headers = new HttpHeaders().set('x-api-key', environment.angelosAppApiKey);
    const body = { eventType: eventType, metadata: metadata, orgID: this.orgId };
    return this.http.post<any>(this.url + "/event/create", body, { headers });
  }
}
