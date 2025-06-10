import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PrivacyEnComponent } from './privacy.component';

describe('PrivacyComponent', () => {
  let component: PrivacyEnComponent;
  let fixture: ComponentFixture<PrivacyEnComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PrivacyEnComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PrivacyEnComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
