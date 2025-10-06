import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TopicSelection } from './topic-selection';

describe('TopicSelection', () => {
  let component: TopicSelection;
  let fixture: ComponentFixture<TopicSelection>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TopicSelection]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TopicSelection);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
