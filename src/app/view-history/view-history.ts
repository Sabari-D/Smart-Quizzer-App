import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, DatePipe, isPlatformBrowser } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Router, RouterModule } from '@angular/router';

// Interface matching the backend's QuizSession.to_dict()
interface HistoryRecord {
  id: number;
  score: number;
  total: number;
  topic: string;
  difficulty: string;
  completed_at: string;
  details: any[]; 
}

@Component({
  selector: 'app-view-history',
  standalone: true,
  imports: [CommonModule, HttpClientModule, RouterModule, DatePipe], 
  templateUrl: './view-history.html',
  styleUrls: ['./view-history.css'],
  providers: [DatePipe] 
})
export class ViewHistoryComponent implements OnInit {
  
  historyRecords: HistoryRecord[] = [];
  loading: boolean = true;
  errorMessage: string = '';
  username: string = '';
  
  // New properties for analytics display
  totalQuizzes: number = 0;
  averageScorePercent: number = 0;
  performanceChange: { status: 'improving' | 'declining' | 'stable', percentage: number, quote: string } = {
    status: 'stable',
    percentage: 0,
    quote: "Keep going!"
  };
  
  private apiUrl = 'http://localhost:5000/api/history/'; 

  constructor(
    private http: HttpClient, 
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object 
  ) { }

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
        const userJson = localStorage.getItem('current_user');
        if (userJson) {
          this.username = JSON.parse(userJson).username;
          this.fetchUserHistory(this.username); 
        } else {
          this.errorMessage = "Session expired. Please log in again.";
          this.loading = false;
          this.router.navigate(['/login']);
        }
    } else {
        this.loading = false;
    }
  }
  
  fetchUserHistory(username: string): void {
    this.loading = true;
    const fetchUrl = `${this.apiUrl}${username}`; 
    
    this.http.get<HistoryRecord[]>(fetchUrl).subscribe({
      next: (data) => {
        this.historyRecords = data;
        this.loading = false;
        
        // CRITICAL: Process analytics after data fetch
        this.calculateAnalytics(data); 
      },
      error: (err) => {
        this.errorMessage = "Could not load history. Server error.";
        this.loading = false;
        console.error("History Fetch Error:", err);
      }
    });
  }

  /**
   * Calculates overall average and the improvement/decline percentage.
   */
  calculateAnalytics(sessions: HistoryRecord[]): void {
    this.totalQuizzes = sessions.length;
    if (sessions.length === 0) return;

    // 1. Calculate overall average
    const totalPossible = sessions.reduce((sum, s) => sum + s.total, 0);
    const totalScore = sessions.reduce((sum, s) => sum + s.score, 0);
    this.averageScorePercent = totalPossible > 0 ? Math.round((totalScore / totalPossible) * 100) : 0;

    if (sessions.length < 2) {
        this.performanceChange = { status: 'stable', percentage: 0, quote: "Start a second quiz to track your improvement!" };
        return;
    }
    
    // 2. Calculate improvement trend (comparing first and last quiz)
    // Sessions are ordered DESC (newest first). sessions[0] is newest.
    const newestSession = sessions[0];
    const oldestSession = sessions[sessions.length - 1];
    
    const newestPercent = (newestSession.score / newestSession.total);
    const oldestPercent = (oldestSession.score / oldestSession.total);

    const percentChange = newestPercent - oldestPercent;
    const absChangePercent = Math.abs(percentChange * 100);

    let status: 'improving' | 'declining' | 'stable' = 'stable';
    let quote: string;

    if (percentChange > 0.05) { // Significant improvement (over 5%)
        status = 'improving';
        quote = "Fantastic progress! Your effort is clearly paying off. 🚀";
    } else if (percentChange < -0.05) { // Significant decline
        status = 'declining';
        quote = "Don't worry! Review your materials and try again. Focus is key. 💪";
    } else {
        quote = "Stay consistent! You are building a strong knowledge base.";
    }

    this.performanceChange = { status, percentage: Math.round(absChangePercent), quote };
  }
  
  // Method to navigate back (for the back button)
  goBack(): void {
    this.router.navigate(['/quiz-history']); 
  }
}






// import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
// import { CommonModule, DatePipe, isPlatformBrowser } from '@angular/common';
// import { HttpClient, HttpClientModule } from '@angular/common/http';
// import { Router, RouterModule } from '@angular/router';

// // Interface matching the backend's QuizSession.to_dict()
// interface HistoryRecord {
//   id: number;
//   score: number;
//   total: number;
//   topic: string;
//   difficulty: string;
//   completed_at: string;
//   details: any[]; 
// }

// @Component({
//   selector: 'app-view-history',
//   standalone: true,
//   imports: [CommonModule, HttpClientModule, RouterModule, DatePipe], 
//   templateUrl: './view-history.html',
//   styleUrls: ['./view-history.css'],
//   providers: [DatePipe] 
// })
// export class ViewHistoryComponent implements OnInit {
  
//   historyRecords: HistoryRecord[] = [];
//   loading: boolean = true;
//   errorMessage: string = '';
//   username: string = '';
  
//   // New properties for analytics display
//   totalQuizzes: number = 0;
//   averageScorePercent: number = 0;
//   performanceChange: { status: 'improving' | 'declining' | 'stable', percentage: number, quote: string } = {
//     status: 'stable',
//     percentage: 0,
//     quote: "Keep going!"
//   };
  
//   private apiUrl = 'http://localhost:5000/api/history/'; 

//   constructor(
//     private http: HttpClient, 
//     private router: Router,
//     @Inject(PLATFORM_ID) private platformId: Object 
//   ) { }

//   ngOnInit(): void {
//     if (isPlatformBrowser(this.platformId)) {
//         const userJson = localStorage.getItem('current_user');
//         if (userJson) {
//           this.username = JSON.parse(userJson).username;
//           this.fetchUserHistory(this.username); 
//         } else {
//           this.errorMessage = "Session expired. Please log in again.";
//           this.loading = false;
//           this.router.navigate(['/login']);
//         }
//     } else {
//         this.loading = false;
//     }
//   }
  
//   fetchUserHistory(username: string): void {
//     this.loading = true;
//     const fetchUrl = `${this.apiUrl}${username}`; 
    
//     this.http.get<HistoryRecord[]>(fetchUrl).subscribe({
//       next: (data) => {
//         this.historyRecords = data;
//         this.loading = false;
        
//         // CRITICAL: Process analytics after data fetch
//         this.calculateAnalytics(data); 
//       },
//       error: (err) => {
//         this.errorMessage = "Could not load history. Server error.";
//         this.loading = false;
//         console.error("History Fetch Error:", err);
//       }
//     });
//   }

//   /**
//    * Calculates overall average and the improvement/decline percentage.
//    */
//   calculateAnalytics(sessions: HistoryRecord[]): void {
//     this.totalQuizzes = sessions.length;
//     if (sessions.length === 0) return;

//     // 1. Calculate overall average
//     const totalPossible = sessions.reduce((sum, s) => sum + s.total, 0);
//     const totalScore = sessions.reduce((sum, s) => sum + s.score, 0);
//     this.averageScorePercent = totalPossible > 0 ? Math.round((totalScore / totalPossible) * 100) : 0;

//     if (sessions.length < 2) {
//         this.performanceChange = { status: 'stable', percentage: 0, quote: "Start a second quiz to track your improvement!" };
//         return;
//     }
    
//     // 2. Calculate improvement trend (comparing first and last quiz)
//     // Sessions are ordered DESC (newest first). sessions[0] is newest.
//     const newestSession = sessions[0];
//     const oldestSession = sessions[sessions.length - 1];
    
//     const newestPercent = (newestSession.score / newestSession.total);
//     const oldestPercent = (oldestSession.score / oldestSession.total);

//     const percentChange = newestPercent - oldestPercent;
//     const absChangePercent = Math.abs(percentChange * 100);

//     let status: 'improving' | 'declining' | 'stable' = 'stable';
//     let quote: string;

//     if (percentChange > 0.05) { // Significant improvement (over 5%)
//         status = 'improving';
//         quote = "Fantastic progress! Your effort is clearly paying off. 🚀";
//     } else if (percentChange < -0.05) { // Significant decline
//         status = 'declining';
//         quote = "Don't worry! Review your materials and try again. Focus is key. 💪";
//     } else {
//         quote = "Stay consistent! You are building a strong knowledge base.";
//     }

//     this.performanceChange = { status, percentage: Math.round(absChangePercent), quote };
//   }

//   /**
//    * View detailed session results
//    */
//   viewSessionDetails(record: HistoryRecord): void {
//     // Store the selected session in sessionStorage for the details page
//     sessionStorage.setItem('selected_session', JSON.stringify(record));
//     // You can create a separate component for session details or show in a modal
//     alert(`Session Details:\nScore: ${record.score}/${record.total}\nTopic: ${record.topic}\nDate: ${new Date(record.completed_at).toLocaleString()}`);
//     // Alternatively, navigate to a details page:
//     // this.router.navigate(['/session-details', record.id]);
//   }
  
//   // Method to navigate back (for the back button)
//   goBack(): void {
//     this.router.navigate(['/quiz-history']); 
//   }
// }