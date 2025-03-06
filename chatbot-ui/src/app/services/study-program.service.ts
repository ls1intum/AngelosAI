import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { StudyProgram } from '../data/study-program';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class StudyProgramService {
  private url = environment.angelosUrl;
  private orgId: number = environment.organisation;
  private filterByOrg: boolean = environment.filterByOrg;

  constructor(private http: HttpClient) { }

  getStudyPrograms(): Observable<StudyProgram[]> {
    const token = sessionStorage.getItem('access_token');

    if (!token) {
      throw new Error('User is not authenticated.');
    }

    const headers = new HttpHeaders().set('ChatAuth', `Bearer ${token}`);

    const params = { filterByOrg: this.filterByOrg.toString() };
    const url = `${this.url}/study-programs/${this.orgId}`;

    return this.http.get<StudyProgram[]>(url, { headers, params });
  }
}
