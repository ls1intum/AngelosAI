import { ComponentFixture, TestBed } from '@angular/core/testing';

import { QACellComponent } from './qacell.component';

describe('QACellComponent', () => {
  let component: QACellComponent;
  let fixture: ComponentFixture<QACellComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [QACellComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(QACellComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
