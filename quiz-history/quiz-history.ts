// import { Component, OnInit } from '@angular/core';
// import { CommonModule } from '@angular/common';
// import { RouterModule } from '@angular/router';

// interface ResultData {
//   score: number;
//   total: number;
// }

// @Component({
//   selector: 'app-quiz-history',
//   standalone: true,
//   imports: [CommonModule, RouterModule],
//   // FIX: Corrected URL to match non-standard filename
//   templateUrl: './quiz-history.html',
//   // FIX: Corrected URL to match non-standard filename
//   styleUrls: ['./quiz-history.css'] 
// })
// export class QuizHistoryComponent implements OnInit {
  
//   quizResults: any[] = [];
//   finalScore: ResultData = { score: 0, total: 0 };

//   constructor() { }

//   ngOnInit(): void {
//     // Retrieve data from session storage
//     const resultsJson = sessionStorage.getItem('quiz_results');
//     const scoreJson = sessionStorage.getItem('final_score');
    
//     if (resultsJson) {
//       this.quizResults = JSON.parse(resultsJson);
//     }
//     if (scoreJson) {
//       this.finalScore = JSON.parse(scoreJson);
//     }
//     console.log("Quiz History Loaded:", this.quizResults);
//   }
  
//   /**
//    * Helper to determine CSS class for score display.
//    * Relies on the CSS classes: .correct, .incorrect, .unscored
//    */
//   getAnswerClass(isCorrect: boolean | undefined): string {
//     // FIX: Simplified return values to match CSS class names (correct, incorrect, unscored)
//     if (isCorrect === true) return 'correct';
//     if (isCorrect === false) return 'incorrect';
//     return 'unscored'; // Used for descriptive questions (manual review)
//   }
// }




// import { Component, OnInit } from '@angular/core';
// import { CommonModule } from '@angular/common';
// import { RouterModule } from '@angular/router';

// interface ResultData {
//   score: number;
//   total: number;
// }

// @Component({
//   selector: 'app-quiz-history',
//   standalone: true,
//   imports: [CommonModule, RouterModule],
//   // FIX: Corrected URL to match non-standard filename
//   templateUrl: './quiz-history.html',
//   // FIX: Corrected URL to match non-standard filename
//   styleUrls: ['./quiz-history.css'] 
// })
// export class QuizHistoryComponent implements OnInit {
  
//   quizResults: any[] = [];
//   finalScore: ResultData = { score: 0, total: 0 };

//   constructor() { }

//   ngOnInit(): void {
//     // Retrieve data from session storage (safe for browser environment)
//     const resultsJson = sessionStorage.getItem('quiz_results');
//     const scoreJson = sessionStorage.getItem('final_score');
    
//     if (resultsJson) {
//       this.quizResults = JSON.parse(resultsJson);
//     }
//     if (scoreJson) {
//       this.finalScore = JSON.parse(scoreJson);
//     }
//     console.log("Quiz History Loaded:", this.quizResults);
//   }
  
//   /**
//    * Helper to determine CSS class for score display.
//    * Returns: 'correct', 'incorrect', or 'unscored' (for manual review/descriptive types).
//    */
//   getAnswerClass(isCorrect: boolean | undefined): string {
//     // This logic is correct and aligns with the CSS classes:
//     if (isCorrect === true) return 'correct';
//     if (isCorrect === false) return 'incorrect';
//     return 'unscored'; // Descriptive questions will have isCorrect as undefined.
//   }
// }



import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

interface ResultData {
  score: number;
  total: number;
}

@Component({
  selector: 'app-quiz-history',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './quiz-history.html',
  styleUrls: ['./quiz-history.css']
})
export class QuizHistoryComponent implements OnInit {
  
  quizResults: any[] = [];
  finalScore: ResultData = { score: 0, total: 0 };

  constructor() {}

  ngOnInit(): void {
    // Retrieve stored quiz results and score from session storage
    const resultsJson = sessionStorage.getItem('quiz_results');
    const scoreJson = sessionStorage.getItem('final_score');
    
    if (resultsJson) {
      this.quizResults = JSON.parse(resultsJson);
    }
    if (scoreJson) {
      this.finalScore = JSON.parse(scoreJson);
    }

    console.log("✅ Quiz History Loaded:", this.quizResults);
  }
  
  /**
   * Returns a CSS class based on the correctness of an answer.
   * Matches the neon glow styles defined in quiz-history.css.
   */
  getAnswerClass(isCorrect: boolean | undefined): string {
    if (isCorrect === true) return 'correct-answer';      // green neon glow
    if (isCorrect === false) return 'incorrect-answer';   // red neon glow
    return ''; // descriptive/unscored question (no glow)
  }
}

