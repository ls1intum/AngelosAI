import { CommonModule, NgClass, NgComponentOutlet, NgFor, NgForOf, NgIf } from '@angular/common';
import { AfterViewInit, Component, Injector, Input, OnChanges, SimpleChanges, TemplateRef, Type, ViewChild } from '@angular/core';
import { MatTableDataSource, MatTableModule } from '@angular/material/table'
import { MatCardModule } from '@angular/material/card'
import { StudyProgram } from '../../../data/model/study-program.model';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';

@Component({
  selector: 'app-main-table',
  standalone: true,
  imports: [
    MatTableModule,
    NgIf,
    NgFor,
    NgForOf,
    CommonModule,
    MatCardModule,
    NgComponentOutlet,
    NgClass,
    MatPaginatorModule,
    MatSortModule
  ],
  templateUrl: './main-table.component.html',
  styleUrl: './main-table.component.css'
})
export class MainTableComponent<T> implements AfterViewInit, OnChanges {
  @Input() dataSource: T[] = [];

  matDataSource = new MatTableDataSource<T>();

  @Input() columns: TableColumn<T>[] = [];
  @Input() parentComponent: any;
  @Input() availableStudyPrograms: StudyProgram[] = [];

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  get displayedColumns(): string[] {
    return this.columns.map(column => column.key as string);
  }

  constructor(private injector: Injector) {}

  createInjector(element: T, column: TableColumn<T>): Injector {
    const rowIndex = this.dataSource.indexOf(element);
    const uniqueID = `sp-add-${rowIndex}`;
  
    return Injector.create({
      providers: [
        { provide: 'cellData', useValue: element },
        { provide: 'cellValue', useValue: column.value ? column.value(element) : element[column.key] },
        { provide: 'parentComponent', useValue: this.parentComponent },
        { provide: 'uniqueID', useValue: uniqueID },
      ],
      parent: this.injector,
    });
  }

  trackByFn(index: number, item: any): any {
    return item.id;
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['dataSource'] && changes['dataSource'].currentValue) {
      this.matDataSource.data = changes['dataSource'].currentValue;
    }

    this.matDataSource.sortingDataAccessor = (row: T, property: string) => {
      const col = this.columns.find(c => c.key === property);
      if (!col) return ''; // unknown column

      const raw =
        col.sortAccessor?.(row) ??
        col.value?.(row) ??
        (row as any)[property];

      // normalize for consistent sorting
      if (raw === null || raw === undefined) return '';
      if (typeof raw === 'boolean') return raw ? 1 : 0;
      if (typeof raw === 'string') return raw.toLowerCase().trim();
      return raw as any;
    };
  }

  ngAfterViewInit(): void {
    this.matDataSource.paginator = this.paginator;
    this.matDataSource.sort = this.sort;
  }
}

export interface TableColumn<T> {
  key: keyof T & string;
  header: string;
  value?: (row: T) => string | number | boolean;
  cellComponent?: Type<any>;
  primary?: boolean;

  sort?: boolean;
  sortAccessor?: (row: T) => string | number | boolean | null | undefined;
}
