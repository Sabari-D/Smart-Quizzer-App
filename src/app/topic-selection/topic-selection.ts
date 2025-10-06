// import { Component, OnInit } from '@angular/core';
// import { HttpClient, HttpClientModule } from '@angular/common/http';
// import { FormsModule } from '@angular/forms';
// import { CommonModule } from '@angular/common';

// @Component({
//   selector: 'app-topic-selection',
//   standalone: true,
//   imports: [CommonModule, FormsModule, HttpClientModule],
//   templateUrl: './topic-selection.component.html',
//   styleUrls: ['./topic-selection.component.css']
// })
// export class TopicSelectionComponent implements OnInit {

//   // Model matching the form fields in the screenshot
//   formData = {
//     name: '',
//     skillLevel: 'Beginner',
//     mode: 'topic', // 'topic' or 'paragraph'
//     subjectOrContent: '',
//     numQuizzes: 5,
//     loading: false,
//     errorMessage: '',
//     quizResult: null as any
//   };

//   // Lists for dropdowns
//   skillLevels: string[] = ['Beginner', 'Intermediate', 'Advanced'];
  
//   // NOTE: In a real app, topics would come from a backend API, but here we hardcode for structure
//   topicOptions: string[] = ['Physics: Quantum Mechanics', 'Programming: Python Basics', 'History: World War II', 'General Knowledge']; 

//   // Map front-end mode to backend 'choice' parameter
//   private backendChoiceMap = {
//     'topic': '1',       // Maps to backend 'subject'
//     'paragraph': '2'    // Maps to backend 'concept'
//   }
  
//   private apiUrl = 'http://127.0.0.1:5000/api/topic-selection';

//   constructor(private http: HttpClient) { }

//   ngOnInit(): void {
//     // Attempt to load the username from local storage after successful login
//     const user = localStorage.getItem('current_user');
//     if (user) {
//         // Automatically fill the name field from the logged-in user
//         this.formData.name = JSON.parse(user).username || ''; 
//     }
//   }

//   /**
//    * Handles form submission to generate the quiz.
//    */
//   onSubmit(): void {
//     this.formData.errorMessage = '';
//     this.formData.quizResult = null;

//     if (!this.formData.subjectOrContent) {
//       this.formData.errorMessage = 'Please enter content or select a topic.';
//       return;
//     }

//     this.formData.loading = true;

//     // Construct the payload matching the /api/topic-selection route in app.py
//     const payload: any = {
//       name: this.formData.name,
//       skill_level: this.formData.skillLevel,
//       choice: this.backendChoiceMap[this.formData.mode],
//       num_quizzes: this.formData.numQuizzes,
//     };

//     // Assign input to 'subject' (for topic) or 'concept' (for paragraph/content)
//     if (this.formData.mode === 'topic') {
//       payload.subject = this.formData.subjectOrContent;
//     } else {
//       payload.concept = this.formData.subjectOrContent;
//       // When using content/paragraph mode, the AI determines the number of questions, 
//       // but we still pass num_quizzes to satisfy the backend validation.
//     }

//     this.http.post(this.apiUrl, payload)
//       .subscribe({
//         next: (response) => {
//           this.formData.loading = false;
//           this.formData.quizResult = response.quiz;
//           console.log('Quiz Generated:', response);
//           alert('Quiz Generated! Check the console for data.');
//         },
//         error: (err) => {
//           this.formData.loading = false;
//           this.formData.errorMessage = err.error?.message || 'Failed to generate quiz.';
//           console.error('API Error:', err);
//         }
//       });
//   }
// }

// import { Component, OnInit } from '@angular/core';
// import { HttpClient, HttpClientModule } from '@angular/common/http';
// import { FormsModule } from '@angular/forms';
// import { CommonModule } from '@angular/common';
// import { Router } from '@angular/router'; // Assuming you'll need the router eventually

// // Define the component and its dependencies
// @Component({
//   selector: 'app-topic-selection',
//   standalone: true,
//   imports: [CommonModule, FormsModule, HttpClientModule],
//   templateUrl: './topic-selection.component.html',
//   styleUrls: ['./topic-selection.component.css']
// })
// export class TopicSelectionComponent implements OnInit {

//   // Data model matching the form fields
//   formData = {
//     name: '',
//     skillLevel: 'Beginner',
//     mode: 'topic' as 'topic' | 'paragraph', // Initialize with a literal type
//     subjectOrContent: '',
//     numQuizzes: 5,
//     loading: false,
//     errorMessage: '',
//     quizResult: null as any
//   };

//   // Type-safe mapping object to resolve TS7053 error
//   private backendChoiceMap: { [key in 'topic' | 'paragraph']: string } = {
//     'topic': '1',       // Maps to backend 'subject'
//     'paragraph': '2'    // Maps to backend 'concept'
//   }

//   // Lists for dropdowns
//   skillLevels: string[] = ['Beginner', 'Intermediate', 'Advanced'];
//   topicOptions: string[] = ['Physics: Quantum Mechanics', 'Programming: Python Basics', 'History: World War II', 'General Knowledge']; 

//   private apiUrl = 'http://127.0.0.1:5000/api/topic-selection';

//   constructor(private http: HttpClient, private router: Router) { } // Inject Router

//   ngOnInit(): void {
//     // Attempt to load the username from local storage after successful login
//     const user = localStorage.getItem('current_user');
//     if (user) {
//         // Automatically fill the name field from the logged-in user
//         this.formData.name = JSON.parse(user).username || ''; 
//     }
//   }

//   /**
//    * Handles form submission to generate the quiz.
//    */
//   onSubmit(): void {
//     this.formData.errorMessage = '';
//     this.formData.quizResult = null;

//     if (!this.formData.subjectOrContent) {
//       this.formData.errorMessage = 'Please enter content or select a topic.';
//       return;
//     }

//     this.formData.loading = true;

//     // The key that caused the error is now safely cast as one of the allowed literal keys
//     const modeKey = this.formData.mode as 'topic' | 'paragraph';

//     // Construct the payload matching the /api/topic-selection route in app.py
//     const payload: any = {
//       name: this.formData.name,
//       skill_level: this.formData.skillLevel,
//       // FIX: Use the type-safe key lookup
//       choice: this.backendChoiceMap[modeKey],
//       num_quizzes: this.formData.numQuizzes,
//     };

//     // Assign input to 'subject' (for topic) or 'concept' (for paragraph/content)
//     if (this.formData.mode === 'topic') {
//       payload.subject = this.formData.subjectOrContent;
//     } else {
//       payload.concept = this.formData.subjectOrContent;
//     }

//     this.http.post(this.apiUrl, payload)
//       .subscribe({
//         next: (response) => {
//           this.formData.loading = false;
//           this.formData.quizResult = response.quiz;
//           console.log('Quiz Generated:', response);
//           // In a real application, you would navigate to the quiz page here
//           this.router.navigate(['/quiz-display', {quiz: JSON.stringify(response.quiz)}]);
//         },
//         error: (err) => {
//           this.formData.loading = false;
//           // Safely check for the message property in the error body
//           this.formData.errorMessage = err.error?.message || 'Failed to generate quiz due to API error.';
//           console.error('API Error:', err);
//         }
//       });
//   }
// }

// import { Component, OnInit, PLATFORM_ID, Inject } from '@angular/core'; // <-- ADD Inject and PLATFORM_ID
// import { HttpClient, HttpClientModule } from '@angular/common/http';
// import { FormsModule } from '@angular/forms';
// import { CommonModule, isPlatformBrowser } from '@angular/common'; // <-- ADD isPlatformBrowser
// import { Router } from '@angular/router';

// // 1. Structure of a single quiz question object
// interface QuizQuestion {
//     type: 'mcq' | 'fill_blank' | 'descriptive';
//     question: string;
//     options?: string[];
//     answer: string;
// }

// // 2. Structure of the full successful API response from /api/topic-selection
// interface QuizGenerationResponse {
//     success: boolean;
//     message: string;
//     quiz: QuizQuestion[]; 
// }

// @Component({
//     selector: 'app-topic-selection',
//     standalone: true,
//     imports: [CommonModule, FormsModule, HttpClientModule],
//     templateUrl: './topic-selection.html', 
//     styleUrls: ['./topic-selection.css'] 
// })
// export class TopicSelectionComponent implements OnInit {

//     // Data model matching the form fields
//     formData = {
//         name: '',
//         skillLevel: 'Beginner',
//         mode: 'topic' as 'topic' | 'paragraph',
//         subjectOrContent: '', // Holds the typed topic OR the pasted paragraph
//         numQuizzes: 5,
//         loading: false,
//         errorMessage: '',
//         quizResult: null as QuizQuestion[] | null 
//     };

//     private backendChoiceMap: { [key in 'topic' | 'paragraph']: string } = {
//         'topic': '1',       
//         'paragraph': '2'    
//     }

//     // Lists for dropdowns
//     skillLevels: string[] = ['Beginner', 'Intermediate', 'Advanced'];
    
//     // topicOptions array is removed as requested/no longer needed

//     private apiUrl = 'http://127.0.0.1:5000/api/topic-selection';

//     constructor(
//         private http: HttpClient, 
//         private router: Router,
//         // FIX: Inject PLATFORM_ID to determine if code is running in a browser
//         @Inject(PLATFORM_ID) private platformId: Object 
//     ) { } 

//     ngOnInit(): void {
//         // FIX APPLIED HERE: Check if the application is running in a browser before accessing localStorage
//         if (isPlatformBrowser(this.platformId)) {
//             const user = localStorage.getItem('current_user');
//             if (user) {
//                 // This logic is now safely inside the browser environment check
//                 this.formData.name = JSON.parse(user).username || ''; 
//             }
//         }
//     }

//     onSubmit(): void {
//         this.formData.errorMessage = '';
//         this.formData.quizResult = null;

//         if (!this.formData.subjectOrContent) {
//             this.formData.errorMessage = 'Please enter content or select a topic.';
//             return;
//         }

//         this.formData.loading = true;
//         const modeKey = this.formData.mode as 'topic' | 'paragraph';

//         const payload: any = {
//             name: this.formData.name,
//             skill_level: this.formData.skillLevel,
//             choice: this.backendChoiceMap[modeKey],
//             num_quizzes: this.formData.numQuizzes,
//         };

//         // This logic correctly sends the user's typed input to the backend
//         if (this.formData.mode === 'topic') {
//             payload.subject = this.formData.subjectOrContent;
//         } else {
//             payload.concept = this.formData.subjectOrContent;
//         }

//         this.http.post<QuizGenerationResponse>(this.apiUrl, payload) 
//             .subscribe({
//                 next: (response) => {
//                     this.formData.loading = false;
//                     this.formData.quizResult = response.quiz; 
//                     console.log('Quiz Generated:', response);
//                     this.router.navigate(['/quiz-display', {quiz: JSON.stringify(response.quiz)}]);
//                 },
//                 error: (err) => {
//                     this.formData.loading = false;
//                     this.formData.errorMessage = err.error?.message || 'Failed to generate quiz due to API error.';
//                     console.error('API Error:', err);
//                 }
//             });
//     }
// }



// import { Component, OnInit, PLATFORM_ID, Inject } from '@angular/core';
// import { HttpClient, HttpClientModule } from '@angular/common/http';
// import { FormsModule } from '@angular/forms';
// import { CommonModule, isPlatformBrowser } from '@angular/common';
// import { Router } from '@angular/router';

// // 1. Structure of a single quiz question object (for local use)
// interface QuizQuestion {
//     type: 'mcq' | 'fill_blank' | 'descriptive';
//     question: string;
//     options?: string[];
//     answer: string;
// }

// // 2. Structure of the full successful API response
// interface QuizGenerationResponse {
//     success: boolean;
//     message: string;
//     quiz: QuizQuestion[]; 
// }

// @Component({
//     selector: 'app-topic-selection',
//     standalone: true,
//     imports: [CommonModule, FormsModule, HttpClientModule],
//     templateUrl: './topic-selection.html', 
//     styleUrls: ['./topic-selection.css'] 
// })
// export class TopicSelectionComponent implements OnInit {

//     // --- CRITICAL FIX: ALL PROPERTIES DECLARED HERE ---
    
//     formData = { // <-- This is correctly placed inside the class
//         name: '',
//         skillLevel: 'Beginner',
//         mode: 'topic' as 'topic' | 'paragraph',
//         subjectOrContent: '',
//         numQuizzes: 5,
//         loading: false,
//         errorMessage: '',
//         quizResult: null as QuizQuestion[] | null 
//     };

//     private backendChoiceMap: { [key in 'topic' | 'paragraph']: string } = {
//         'topic': '1',       
//         'paragraph': '2'    
//     };

//     skillLevels: string[] = ['Beginner', 'Intermediate', 'Advanced'];
    
//     private apiUrl = 'http://127.0.0.1:5000/api/topic-selection';

//     // --------------------------------------------------

//     constructor(
//         private http: HttpClient,
//         private router: Router,
//         // Injections are correct
//         @Inject(PLATFORM_ID) private platformId: Object 
//     ) { }

//     ngOnInit(): void {
//         // Fetch user data safely inside browser environment check
//         if (isPlatformBrowser(this.platformId)) {
//             const user = localStorage.getItem('current_user');
//             if (user) {
//                 this.formData.name = JSON.parse(user).username || '';
//             }
//         }
//     }

//     onSubmit(): void {
//         this.formData.errorMessage = '';
//         this.formData.quizResult = null;

//         if (!this.formData.subjectOrContent) {
//             this.formData.errorMessage = 'Please enter content or select a topic.';
//             return;
//         }

//         this.formData.loading = true;
//         const modeKey = this.formData.mode as 'topic' | 'paragraph';

//         const payload: any = {
//             name: this.formData.name,
//             skill_level: this.formData.skillLevel,
//             choice: this.backendChoiceMap[modeKey],
//             num_quizzes: this.formData.numQuizzes,
//         };

//         if (this.formData.mode === 'topic') {
//             payload.subject = this.formData.subjectOrContent;
//         } else {
//             payload.concept = this.formData.subjectOrContent;
//         }

//         this.http.post<QuizGenerationResponse>(this.apiUrl, payload) // Use the defined interface
//             .subscribe({
//                 next: (response) => {
//                     this.formData.loading = false;

//                     // FIX 1: Store the quiz data in session storage
//                     if (isPlatformBrowser(this.platformId)) {
//                         sessionStorage.setItem('active_quiz_data', JSON.stringify(response.quiz));
//                     }

//                     console.log('Quiz Generated. Initiating redirect...');

//                     // FIX 2: Use the simplest, most reliable absolute path navigation
//                     this.router.navigate(['/quiz']); 
//                 },
//                 error: (err) => {
//                     this.formData.loading = false;
//                     this.formData.errorMessage = err.error?.message || 'Failed to generate quiz due to API error.';
//                     console.error('API Error:', err);
//                 }
//             });
//     }
// }

import { Component, OnInit, PLATFORM_ID, Inject } from '@angular/core';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';

// 1. Structure of a single quiz question object (for local use)
interface QuizQuestion {
    type: 'mcq' | 'fill_blank' | 'descriptive';
    question: string;
    options?: string[];
    answer: string;
}

// 2. Structure of the full successful API response
interface QuizGenerationResponse {
    success: boolean;
    message: string;
    quiz: QuizQuestion[]; 
}

@Component({
    selector: 'app-topic-selection',
    standalone: true,
    imports: [CommonModule, FormsModule, HttpClientModule],
    templateUrl: './topic-selection.html', 
    styleUrls: ['./topic-selection.css'] 
})
export class TopicSelectionComponent implements OnInit {

    // --- CRITICAL FIX: ALL PROPERTIES DECLARED HERE ---
    
    formData = { // <-- Correct placement inside the class
        name: '',
        skillLevel: 'Beginner',
        mode: 'topic' as 'topic' | 'paragraph',
        subjectOrContent: '',
        numQuizzes: 5,
        loading: false,
        errorMessage: '',
        quizResult: null as QuizQuestion[] | null 
    };

    private backendChoiceMap: { [key in 'topic' | 'paragraph']: string } = {
        'topic': '1',       
        'paragraph': '2'    
    };

    skillLevels: string[] = ['Beginner', 'Intermediate', 'Advanced'];
    
    private apiUrl = 'http://127.0.0.1:5000/api/topic-selection';

    // --------------------------------------------------

    constructor(
        private http: HttpClient,
        private router: Router,
        // Injections are correct
        @Inject(PLATFORM_ID) private platformId: Object 
    ) { }

    ngOnInit(): void {
        // Fetch user data safely inside browser environment check
        if (isPlatformBrowser(this.platformId)) {
            const user = localStorage.getItem('current_user');
            if (user) {
                this.formData.name = JSON.parse(user).username || '';
            }
        }
    }

    onSubmit(): void {
        this.formData.errorMessage = '';
        this.formData.quizResult = null;

        if (!this.formData.subjectOrContent) {
            this.formData.errorMessage = 'Please enter content or select a topic.';
            return;
        }

        this.formData.loading = true;
        const modeKey = this.formData.mode as 'topic' | 'paragraph';

        const payload: any = {
            // Data acquisition is complete and correct
            name: this.formData.name,
            skill_level: this.formData.skillLevel,
            choice: this.backendChoiceMap[modeKey],
            num_quizzes: this.formData.numQuizzes,
        };

        // Conditional payload field logic is correct
        if (this.formData.mode === 'topic') {
            payload.subject = this.formData.subjectOrContent;
        } else {
            payload.concept = this.formData.subjectOrContent;
        }

        this.http.post<QuizGenerationResponse>(this.apiUrl, payload)
            .subscribe({
                next: (response) => {
                    this.formData.loading = false;

                    // FIX 1: Store the quiz data in session storage
                    if (isPlatformBrowser(this.platformId)) {
                        // The quiz data received from Flask's success response is stored here
                        sessionStorage.setItem('active_quiz_data', JSON.stringify(response.quiz));
                    }

                    console.log('Quiz Generated. Initiating redirect...');

                    // FIX 2: Use the simplest, most reliable absolute path navigation
                    this.router.navigate(['/quiz']); 
                },
                error: (err) => {
                    this.formData.loading = false;
                    // Error handling is correct
                    this.formData.errorMessage = err.error?.message || 'Failed to generate quiz due to API error.';
                    console.error('API Error:', err);
                }
            });
    }
}