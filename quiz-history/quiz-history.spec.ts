// import { ComponentFixture, TestBed } from '@angular/core/testing';

// import { QuizHistory } from './quiz-history';

// describe('QuizHistory', () => {
//   let component: QuizHistory;
//   let fixture: ComponentFixture<QuizHistory>;

//   beforeEach(async () => {
//     await TestBed.configureTestingModule({
//       imports: [QuizHistory]
//     })
//     .compileComponents();

//     fixture = TestBed.createComponent(QuizHistory);
//     component = fixture.componentInstance;
//     fixture.detectChanges();
//   });

//   it('should create', () => {
//     expect(component).toBeTruthy();
//   });
// });
// File: src/app/quiz/quiz.spec.ts

// File: src/app/quiz/quiz.spec.ts

// File: src/app/quiz/quiz.spec.ts

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing'; 
import { RouterTestingModule } from '@angular/router/testing';     
import { FormsModule } from '@angular/forms';                       
import { CommonModule } from '@angular/common';                     
import { ActivatedRoute } from '@angular/router';
import { of } from 'rxjs'; 

// FIX: We must try to import the file using its full, actual path if './quiz' fails.
// Since you previously confirmed the file is named quiz.ts:
// Change the import below to explicitly reference the file name that contains the EXPORTED QuizComponent class.
import { QuizComponent } from './quiz'; 

// --- If the above line still fails, you must try the following and restart: ---
// 1. Check your file name in the explorer: Is it quiz.ts or quiz.component.ts?
// 2. If it is quiz.ts, ensure the EXPORT statement is correct in quiz.ts: `export class QuizComponent { ... }`
// 3. Then, try setting a mock provider for the ActivatedRoute *before* the imports list.
// -------------------------------------------------------------------------------


const mockActivatedRoute = {
    paramMap: of({ get: () => null }) 
};

describe('QuizComponent', () => {
    let component: QuizComponent;
    let fixture: ComponentFixture<QuizComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [
                // NOTE: This import assumes your EXPORT is correct in quiz.ts
                QuizComponent,             
                HttpClientTestingModule,   
                RouterTestingModule,     
                FormsModule,             
                CommonModule,
            ],
            providers: [
                { provide: ActivatedRoute, useValue: mockActivatedRoute }
            ]
        })
        .compileComponents();

        fixture = TestBed.createComponent(QuizComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create the quiz component successfully', () => {
        expect(component).toBeTruthy();
    });
    
    it('should initialize with no questions if no data is found', () => {
        expect(component.quizQuestions.length).toBe(0);
    });
});