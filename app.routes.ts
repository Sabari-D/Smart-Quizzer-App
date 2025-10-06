

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
