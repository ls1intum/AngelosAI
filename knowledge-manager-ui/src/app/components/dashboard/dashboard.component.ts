import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatPaginatorIntl, MatPaginatorModule } from '@angular/material/paginator';
import { MatRadioModule } from '@angular/material/radio';
import { MatTableModule } from '@angular/material/table';
import { LimitDTO } from '@app/data/dto/limit.dto';
import { CustomPaginatorIntl } from '@app/layout/paginator/custom-paginator-intl.service';
import { DashboardService } from '@app/services/dashboard.service';
import { ChartConfiguration, ChartType } from 'chart.js';
import { Subject, takeUntil } from 'rxjs';
import { NgChartsModule } from 'ng2-charts';
import { DateTime } from 'luxon';
import { EventLogDTO } from '@app/data/dto/event-log.dto';
import { MainTableComponent, TableColumn } from '@app/layout/tables/main-table/main-table.component';
import { Feedback } from '@app/data/model/feedback.model';
import { MatIconModule } from '@angular/material/icon';
import { FeedbackComponent } from './feedback/feedback.component';
import { FeedbackCellComponent } from '@app/layout/cells/feedback-cell/feedback-cell.component';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { QaLogDTO } from '@app/data/dto/qa-log.dto';
import { QACellComponent } from '@app/layout/cells/qacell/qacell.component';

type TimeFrame = 'today' | 'week' | 'month' | 'total';

type LogMode = 'feedback' | 'qa';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule, FormsModule, ReactiveFormsModule,
    MatRadioModule, MatCardModule, MatTableModule, MatPaginatorModule,
    MainTableComponent,
    NgChartsModule, MatIconModule, MatButtonToggleModule
  ],
  providers: [
    { provide: MatPaginatorIntl, useClass: CustomPaginatorIntl }
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {

  /** --- UI state ---------------------------------------------------- */
  frameCtrl = new FormControl<TimeFrame>('week');
  limits?: LimitDTO;

  // Cards
  chatCount = 0;
  mailSensitive = 0;
  mailAuto = 0;
  posPct = 0;

  // Charts
  lineCfg?: ChartConfiguration<'line'>;
  pieCfg?: ChartConfiguration<'pie'>;

  // Feedback table
  feedbackColumns: TableColumn<Feedback>[] = [
    {
      key: 'date',
      header: 'Datum',
      value: (f: Feedback) => f.date,
      primary: true
    },
    {
      key: 'type',
      header: 'Art',
      cellComponent: FeedbackComponent
    },
    {
      key: 'question',
      header: 'Frage',
      cellComponent: FeedbackCellComponent
    },
    {
      key: 'answer',
      header: 'Antwort',
      cellComponent: FeedbackCellComponent
    },
  ];
  feedbackRows: Feedback[] = [];

  qaColumns: TableColumn<QaLogDTO>[] = [
    {
      key: 'createdAt',
      header: 'Datum',
      value: (f: QaLogDTO) => f.createdAt,
      primary: true
    },
    {
      key: 'question',
      header: 'Frage',
      cellComponent: QACellComponent
    },
    {
      key: 'answer',
      header: 'Antwort',
      cellComponent: QACellComponent
    },
  ];

  logMode: LogMode = 'feedback';

  // Q&A table state
  qaRows: QaLogDTO[] = [];
  qaLoading = false;
  qaLoadedOnce = false;

  private destroy$ = new Subject<void>();

  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    this.loadLimits();
    this.frameCtrl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => this.loadEvents());
    this.loadEvents();
  }

  /** Clean up subscriptions */
  ngOnDestroy(): void { this.destroy$.next(); this.destroy$.complete(); }

  /** ------------ DATA LOADERS ---------------- */
  private loadLimits(): void {
    this.dashboardService.getUsageLimits().subscribe(l => this.limits = l);
  }

  private loadEvents(): void {
    const [from, to] = this.calculateRange(this.frameCtrl.value!);
    let fromDT = DateTime.fromJSDate(from).setLocale('de');
    let toDT = DateTime.fromJSDate(to).setLocale('de');

    this.dashboardService.getEventsInTimeframge(from, to).subscribe(events => {
      // Split lists
      const feedback = events.filter(e => e.eventType.includes('chat_feedback'));
      const usage   = events.filter(e => e.eventType === 'chat_request_completed'
        || e.eventType === 'mail_classified_sensitive'
        || e.eventType === 'mail_classified_nonsensitive');

      // ------ Stats boxes ----------
      this.chatCount = usage.filter(e => e.eventType === 'chat_request_completed').length;
      this.mailSensitive = usage.filter(e => e.eventType === 'mail_classified_sensitive').length;
      this.mailAuto = usage.filter(e => e.eventType === 'mail_classified_nonsensitive').length;

      const pos = feedback.filter(f => f.eventType === 'chat_feedback_positive').length;
      const totalFb = feedback.length || 1;
      this.posPct = Math.round((pos / totalFb) * 100);

      // ------ Line chart ----------
      if (this.frameCtrl.value === 'total') {
        const firstEvent: string = events[0].timestamp;
        const lastEvent: string = events[events.length - 1].timestamp;

        fromDT = DateTime.fromISO(firstEvent);
        toDT = DateTime.fromISO(lastEvent);
      }

      this.prepareLineChart(usage, fromDT, toDT);

      // ------ Pie chart -----------
      this.preparePieChart(pos, totalFb - pos);

      // ------ Feedback table ------
      this.feedbackRows  = feedback.reverse().map(f => {
        let q = '', a = '';
        try {
          const meta = JSON.parse(f.metadata);
          q = meta.question ?? '';
          a = meta.answer ?? '';
        } catch { /* ignore malformed */ }
        return {
          date: DateTime.fromISO(f.timestamp).toLocaleString(DateTime.DATETIME_SHORT),
          type: f.eventType.replace('chat_feedback_', ''),
          question: q, 
          answer: a
        };
      });
    });
  }

  /** ------------ HELPERS ------------------- */
  private calculateRange(t: TimeFrame): [Date, Date] {
    const now = DateTime.now();
    switch (t) {
      case 'today':
        return [now.startOf('day').toJSDate(), now.endOf('day').toJSDate()];
      case 'week':
        return [now.minus({ days: 7 }).toJSDate(), now.endOf('day').toJSDate()];
      case 'month':
        return [now.minus({ days: 30 }).toJSDate(), now.endOf('day').toJSDate()];
      default:
        return [new Date(0), now.toJSDate()];
    }
  }

  private prepareLineChart(usage: EventLogDTO[], start: DateTime, end: DateTime): void {
    if (!usage.length) { 
      this.lineCfg = undefined; 
      return; 
    }
  
    const dayDiff = end.startOf('day').diff(start.startOf('day'), 'days').days;

    const byHour = dayDiff < 2;
  
    const bucketFmt = byHour ? 'HH' : 'yyyy-LL-dd';
    const labelFmt = byHour ? 'HH:mm' : 'dd.LLLL';
  
    const makeSeries = (type: string) => {
      const map = new Map<string, number>();
      usage.filter(e => e.eventType === type).forEach(e => {
        const key = DateTime.fromISO(e.timestamp).toFormat(bucketFmt);
        map.set(key, (map.get(key) ?? 0) + 1);
      });
      return map;
    };
  
    const chats = makeSeries('chat_request_completed');
    const sens  = makeSeries('mail_classified_sensitive');
    const auto  = makeSeries('mail_classified_nonsensitive');
  
    const buckets = this.generateDateBuckets(start, end, byHour, bucketFmt);
  
    const root = getComputedStyle(document.documentElement);
    const chatColor = root.getPropertyValue('--tum-blue-light-dark').trim() || '#779EC4';
    const sensColor = root.getPropertyValue('--third-color').trim() || '#EB5181';
    const autoColor = root.getPropertyValue('--tum-light-blue').trim() || '#4d4c8a';
  
    this.lineCfg = {
      type: 'line',
      data: {
        labels: buckets.map(k => DateTime.fromFormat(k, bucketFmt).setLocale('de').toFormat(labelFmt)),
        datasets: [
          {
            label: 'Chats',
            data: buckets.map(k => chats.get(k) ?? 0),
            borderColor: chatColor,
            backgroundColor: chatColor + '33',
            tension: .3
          },
          {
            label: 'Sensible Mails',
            data: buckets.map(k => sens.get(k) ?? 0),
            borderColor: sensColor,
            backgroundColor: sensColor + '33',
            tension: .3
          },
          {
            label: 'Automatische Mail-Antworten',
            data: buckets.map(k => auto.get(k) ?? 0),
            borderColor: autoColor,
            backgroundColor: autoColor + '33',
            tension: .3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true }
        }
      }
    };
  }

  private preparePieChart(pos: number, neg: number): void {
    this.pieCfg = {
      type: 'pie',
      data: {
        labels: ['Positiv', 'Negativ'],
        datasets: [{
          data: [pos, neg],
          backgroundColor: ['#43a047', '#d32f2f']
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    };
  }

  private generateDateBuckets(
    start: DateTime,
    end: DateTime,
    byHour: boolean,
    bucketFmt: string
  ): string[] {
    const buckets: string[] = [];
    let cursor = byHour
      ? start.startOf('hour')
      : start.startOf('day');
  
    const step = byHour
      ? { hours: 1 }
      : { days: 1 };
  
    // Continue pushing until we pass `end`
    while (cursor <= end) {
      buckets.push(cursor.toFormat(bucketFmt));
      cursor = byHour
        ? cursor.plus({ hours: 1 })
        : cursor.plus({ days: 1 });
    }
  
    return buckets;
  }

  onLogModeChange(mode: LogMode) {
    this.logMode = mode;
    if (mode === 'qa' && !this.qaLoadedOnce) {
      this.qaLoading = true;
      this.dashboardService.getQaLogs().subscribe({
        next: items => {
          // format date once for display
          this.qaRows = items.map(r => ({
            ...r,
            createdAt: DateTime.fromISO(r.createdAt)
              .toLocaleString(DateTime.DATETIME_SHORT)
          }));
          this.qaLoadedOnce = true;
        },
        error: () => { this.qaRows = []; },
        complete: () => { this.qaLoading = false; }
      });
    }
  }
}
