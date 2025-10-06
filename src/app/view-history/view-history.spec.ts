import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewHistory } from './view-history';

describe('ViewHistory', () => {
  let component: ViewHistory;
  let fixture: ComponentFixture<ViewHistory>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ViewHistory]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ViewHistory);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
