// File: src/app/register/register.ts

// import { Component } from '@angular/core';
// import { Location, CommonModule } from '@angular/common';
// import { FormsModule } from '@angular/forms';
// import { HttpClient, HttpErrorResponse } from '@angular/common/http';
// import { Router } from '@angular/router';
// import { PopupService } from '../services/popup'; 

// @Component({
//   selector: 'app-register',
//   standalone: true,
//   imports: [CommonModule, FormsModule],
//   templateUrl: './register.html',
//   styleUrls: ['./register.css']
// })
// export class RegisterComponent {
//   username = '';
//   password = '';
//   confirmPassword = '';
  
//   constructor(
//     private location: Location, 
//     private http: HttpClient,
//     private router: Router,
//     private popupService: PopupService
//   ) {}

//   goBack(): void {
//     this.location.back();
//   }

//   onRegisterSubmit(): void {
//     if (this.password !== this.confirmPassword) {
//       this.popupService.show('Passwords do not match.', true);
//       return;
//     }

//     const userData = {
//       username: this.username,
//       password: this.password,
//       password_confirm: this.confirmPassword
//     };
    
//     const apiUrl = 'http://127.0.0.1:5000/api/register';

//     this.http.post<any>(apiUrl, userData).subscribe({
//       next: (response) => {
//         // SUCCESS: Show message and redirect to login
//         this.popupService.show(response.message);
//         this.router.navigate(['/login']);
//       },
//       error: (err: HttpErrorResponse) => {
//         // FIX: Display the message provided by Flask (e.g., "You are already registered.")
//         const message = err.error?.message || 'Registration failed. Check network.';
//         this.popupService.show(message, true);
//       }
//     });
//   }
// }

import { Component } from '@angular/core';
import { Location, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpErrorResponse, HttpClientModule } from '@angular/common/http';
import { Router, RouterModule } from '@angular/router'; // Ensure RouterModule is available
import { PopupService } from '../services/popup'; 

@Component({
    selector: 'app-register',
    standalone: true,
    // FIX: Added HttpClientModule and RouterModule for full functionality
    imports: [CommonModule, FormsModule, HttpClientModule, RouterModule], 
    templateUrl: './register.html',
    styleUrls: ['./register.css']
})
export class RegisterComponent {
    username = '';
    email = ''; // FIX: Added new property for email
    password = '';
    confirmPassword = '';
    
    constructor(
        private location: Location, 
        private http: HttpClient,
        private router: Router,
        private popupService: PopupService
    ) {}

    goBack(): void {
        this.location.back();
    }

    onRegisterSubmit(): void {
        if (this.password !== this.confirmPassword) {
            this.popupService.show('Passwords do not match.', true);
            return;
        }
        
        // FIX: The payload now includes the email
        const userData = {
            username: this.username,
            email: this.email, 
            password: this.password,
            password_confirm: this.confirmPassword
        };
        
        const apiUrl = 'http://127.0.0.1:5000/api/register';

        this.http.post<any>(apiUrl, userData).subscribe({
            next: (response) => {
                // SUCCESS: Show message and redirect to login
                this.popupService.show(response.message);
                this.router.navigate(['/login']);
            },
            error: (err: HttpErrorResponse) => {
                // FIX: Display the message provided by Flask (e.g., "User already exists.")
                const message = err.error?.message || 'Registration failed. Check network.';
                this.popupService.show(message, true);
            }
        });
    }
}