import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { AuthenticationService } from "./authentication.service";
import { Observable } from "rxjs";
import { EventLogDTO } from "@app/data/dto/event-log.dto";
import { environment } from "environments/environment";
import { LimitDTO } from "@app/data/dto/limit.dto";

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
    constructor(
        private http: HttpClient,
        private authService: AuthenticationService
    ) { }

    /**
     * Fetch all events in a given timeframe for an organisation.
     */
    getEventsInTimeframge(from: Date, to: Date): Observable<EventLogDTO[]> {
      const body = {
        from: from.toISOString(),
        to: to.toISOString()
      };  
      return this.http.post<EventLogDTO[]>(`${environment.backendUrl}/event/timeframe`, body, {})
    }

    /**
     * Fetch configured usage limits from the backend.
     */
    getUsageLimits(): Observable<LimitDTO> {
        return this.http.get<LimitDTO>(`${environment.backendUrl}/event/limits`);
    }
}
  