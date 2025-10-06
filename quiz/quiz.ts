import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';

// Interfaces (Match the backend structure)
interface QuizQuestion {
    // Correct types for all scorable questions
    type: 'mcq' | 'fill_blank' | 'true_false' | 'multi_select'; 
    question: string;
    options?: string[];
    answer: string; 
    userAnswer?: string; 
    isCorrect?: boolean; 
}

@Component({
    selector: 'app-quiz',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule], 
    templateUrl: './quiz.html',
    styleUrls: ['./quiz.css']
})
export class QuizComponent implements OnInit {
    
    quizQuestions: QuizQuestion[] = [];
    currentQuestionIndex: number = 0;
    quizCompleted: boolean = false;
    
    selectedOption: string = ''; // Used for binding single-select radio buttons
    checkedOptions: string[] = []; // ADDED: Property to hold checked options for multi-select

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        @Inject(PLATFORM_ID) private platformId: Object
    ) { }

    ngOnInit(): void {
        // FIX: Check if we are in the browser environment
        if (isPlatformBrowser(this.platformId)) {
            const quizJson = sessionStorage.getItem('active_quiz_data');
            
            if (quizJson) {
                this.quizQuestions = JSON.parse(quizJson);
                this.quizQuestions.forEach(q => q.userAnswer = '');
                console.log("Quiz Loaded:", this.quizQuestions);
                
                sessionStorage.removeItem('active_quiz_data'); 
                
            } else {
                this.router.navigate(['/topic-selection']);
            }
        } else {
            console.log("QuizComponent initialized on server side.");
        }
    }

    /**
     * Toggles the selection status for multi-select checkboxes.
     */
    toggleCheckbox(option: string): void {
        const index = this.checkedOptions.indexOf(option);
        if (index > -1) {
            this.checkedOptions.splice(index, 1); // Remove if already checked
        } else {
            this.checkedOptions.push(option); // Add if not checked
        }
    }


    /**
     * Moves to the next question, saving the user's answer.
     */
    nextQuestion(): void {
        const currentQ = this.quizQuestions[this.currentQuestionIndex];
        
        // 1. Save the answer based on type
        if (currentQ.type === 'mcq' || currentQ.type === 'true_false') {
            currentQ.userAnswer = this.selectedOption;
        } else if (currentQ.type === 'multi_select') {
            // FIX: Join the selected checkboxes into a comma-separated string
            currentQ.userAnswer = this.checkedOptions.sort().join(', '); 
        }
        
        // 2. Reset selection states for the next question
        this.selectedOption = '';
        this.checkedOptions = []; // CRITICAL: Clear checkbox array for next question

        // 3. Move index
        if (this.currentQuestionIndex < this.quizQuestions.length - 1) {
            this.currentQuestionIndex++;
        } else {
            this.submitQuiz();
        }
    }

    /**
     * Calculates scores and navigates to the Quiz History page.
     */
    submitQuiz(): void {
        // Ensure this only runs in the browser
        if (!isPlatformBrowser(this.platformId)) return;
        
        let score = 0;
        
        // 1. Evaluate all questions
        this.quizQuestions.forEach(q => {
            let isCorrect = false;
            const userAnswer = (q.userAnswer || '').trim().toLowerCase();
            const modelAnswer = q.answer.trim().toLowerCase();

            // SCORING LOGIC
            if (q.type === 'multi_select') {
                // For multi-select: sort both arrays and compare the resulting strings
                const userArray = userAnswer.split(',').map(s => s.trim()).sort().join(',');
                const modelArray = modelAnswer.split(',').map(s => s.trim()).sort().join(',');
                isCorrect = (userArray === modelArray);
                
            } else {
                // Standard check for mcq, fill_blank, true_false
                isCorrect = (userAnswer === modelAnswer);
            }
            
            q.isCorrect = isCorrect;
            if (isCorrect) { score++; }
        });

        this.quizCompleted = true;
        console.log(`Quiz Finished. Score: ${score}/${this.quizQuestions.length}`);

        // 2. Store results in session storage for the history page to access
        sessionStorage.setItem('quiz_results', JSON.stringify(this.quizQuestions));
        sessionStorage.setItem('final_score', JSON.stringify({
            score: score,
            total: this.quizQuestions.length
        }));

        // 3. Redirect to the history page
        this.router.navigate(['/quiz-history']);
    }
}