// import { Routes } from '@angular/router';
// import { WelcomeComponent } from './welcome/welcome';
// import { RegisterComponent } from './register/register';
// import { LoginComponent } from './login/login';
// import { ExitComponent } from './exit/exit';
// // FIX: Imports the TopicSelection component
// import { TopicSelectionComponent } from './topic-selection/topic-selection'; 
// import { QuizComponent } from './quiz/quiz'; // Import the new component
// import { QuizHistoryComponent } from './quiz-history/quiz-history';
// import { ForgotPasswordComponent } from './forgot-password/forgot-password';  

// export const routes: Routes = [
//     // Default redirect
//     { path: '', redirectTo: '/welcome', pathMatch: 'full' }, 

//     // Main Application Routes
//     { path: 'welcome', component: WelcomeComponent },
//     { path: 'register', component: RegisterComponent },
//     { path: 'login', component: LoginComponent },
//     { path: 'exit', component: ExitComponent },
//     // Add this line to your routes array:
// { path: 'forgot-password', component: ForgotPasswordComponent },
    
//     // The target route for successful login redirect
//     { path: 'topic-selection', component: TopicSelectionComponent } ,
//      // 1. Route for the active quiz (Receives data via route parameter)
//     { path: 'quiz', component: QuizComponent }, 
    
//     // 2. Route for the history/results page
//     { path: 'quiz-history', component: QuizHistoryComponent }
// ];

// import { Routes } from '@angular/router';
// import { WelcomeComponent } from './welcome/welcome';
// import { RegisterComponent } from './register/register';
// import { LoginComponent } from './login/login';
// import { ExitComponent } from './exit/exit';
// import { TopicSelectionComponent } from './topic-selection/topic-selection'; 
// import { QuizComponent } from './quiz/quiz'; 
// import { QuizHistoryComponent } from './quiz-history/quiz-history';
// import { ForgotPasswordComponent } from './forgot-password/forgot-password'; 
// // FIX: Add import for the new ResetPasswordComponent
// import { ResetPasswordComponent } from './reset-password/reset-password'; 

// export const routes: Routes = [
//     // Default redirect
//     { path: '', redirectTo: '/welcome', pathMatch: 'full' }, 

//     // Main Application Routes
//     { path: 'welcome', component: WelcomeComponent },
//     { path: 'register', component: RegisterComponent },
//     { path: 'login', component: LoginComponent },
//     { path: 'exit', component: ExitComponent },
    
//     // FIX 1: Forgot Password Request Form
//     { path: 'forgot-password', component: ForgotPasswordComponent },
    
//     // FIX 2: Password Reset Form (Receives token via query params or path)
//     { path: 'reset-password', component: ResetPasswordComponent }, 
    
//     // The target route for successful login redirect
//     { path: 'topic-selection', component: TopicSelectionComponent } ,
    
//     // Quiz Routes
//     { path: 'quiz', component: QuizComponent }, 
//     { path: 'quiz-history', component: QuizHistoryComponent }
// ];


import { Routes } from '@angular/router';
import { WelcomeComponent } from './welcome/welcome';
import { RegisterComponent } from './register/register';
import { LoginComponent } from './login/login';
import { ExitComponent } from './exit/exit';
import { TopicSelectionComponent } from './topic-selection/topic-selection'; 
import { QuizComponent } from './quiz/quiz'; 
import { QuizHistoryComponent } from './quiz-history/quiz-history';
import { ForgotPasswordComponent } from './forgot-password/forgot-password'; 
import { ResetPasswordComponent } from './reset-password/reset-password'; 

// CRITICAL FIX: Import the new component for OTP verification
import { VerifyOtpComponent } from './verify-otp/verify-otp'; 
import { ViewHistoryComponent } from './view-history/view-history';


export const routes: Routes = [
    // Default redirect
    { path: '', redirectTo: '/welcome', pathMatch: 'full' }, 

    // Main Application Routes
    { path: 'welcome', component: WelcomeComponent },
    { path: 'register', component: RegisterComponent },
    { path: 'login', component: LoginComponent },
    { path: 'exit', component: ExitComponent },
    
    // 1. Initial Request Form (Gets email or mobile number)
    { path: 'forgot-password', component: ForgotPasswordComponent },
    
    // 2. OTP Verification Step (New step for mobile resets)
    { path: 'verify-otp', component: VerifyOtpComponent }, 
    
    // 3. Final Password Reset Form (Uses the secure token)
    { path: 'reset-password', component: ResetPasswordComponent }, 
    
    // The target route for successful login redirect
    { path: 'topic-selection', component: TopicSelectionComponent } ,
    
    // Quiz Routes
    { path: 'quiz', component: QuizComponent }, 
    { path: 'quiz-history', component: QuizHistoryComponent },
     { path: 'view-history', component: ViewHistoryComponent } 
];