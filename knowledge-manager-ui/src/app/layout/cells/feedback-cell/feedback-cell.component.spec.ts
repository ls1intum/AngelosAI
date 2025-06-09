import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FeedbackCellComponent } from './feedback-cell.component';

describe('FeedbackCellComponent', () => {
  let component: FeedbackCellComponent;
  let fixture: ComponentFixture<FeedbackCellComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FeedbackCellComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FeedbackCellComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
