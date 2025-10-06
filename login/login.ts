// File: src/app/login/login.ts

// import { Component, OnInit } from '@angular/core';
// import { Location, CommonModule } from '@angular/common';
// import { FormsModule } from '@angular/forms';
// import { HttpClient, HttpClientModule } from '@angular/common/http';
// import { Router } from '@angular/router'; 
// import { PopupService } from '../services/popup'; // Assuming this is also used here

// interface LoginResponse {
//     success: boolean;
//     message: string;
//     user: { id: number; username: string; created_at: string; is_admin?: boolean; };
// }

// @Component({
//   selector: 'app-login',
//   standalone: true,
//   imports: [CommonModule, FormsModule, HttpClientModule], 
//   templateUrl: './login.html',
//   styleUrls: ['./login.css']
// })
// export class LoginComponent implements OnInit {

//   loginData = { username: '', password: '' };
//   errorMessage: string = '';
//   loading: boolean = false;
//   private apiUrl = 'http://127.0.0.1:5000/api/login'; 

//   constructor(
//     private location: Location, 
//     private http: HttpClient,
//     private router: Router,
//     private popupService: PopupService
//   ) {}

//   ngOnInit(): void { }

//   onLoginSubmit(): void {
//     this.errorMessage = '';
    
//     if (!this.loginData.username || !this.loginData.password) {
//       this.errorMessage = 'Username and password are required.';
//       return;
//     }

//     this.loading = true;

//     this.http.post<LoginResponse>(this.apiUrl, this.loginData)
//       .subscribe({
//         next: (response) => {
//           this.loading = false;
//           // SUCCESS: Store user data and redirect
//           localStorage.setItem('current_user', JSON.stringify(response.user));
//           this.popupService.show(response.message);
//           this.router.navigate(['/topic-selection']);
//         },
//         error: (err) => {
//           this.loading = false;
//           // FIX: Display the exact error message from Flask
//           this.errorMessage = err.error?.message || 'Login failed. An unknown error occurred.';
//           this.popupService.show(this.errorMessage, true);
//           console.error('Login Error:', err);
//         }
//       });
//   }

//   goBack(): void {
//     this.location.back();
//   }
// }

// File: src/app/login/login.ts

import { Component, OnInit } from '@angular/core';
import { Location, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Router, RouterModule } from '@angular/router'; // FIX: IMPORT RouterModule HERE
import { PopupService } from '../services/popup'; 

interface LoginResponse {
    success: boolean;
    message: string;
    user: { id: number; username: string; created_at: string; is_admin?: boolean; };
}

@Component({
    selector: 'app-login',
    standalone: true,
    // FIX: ADD RouterModule to the imports array to enable [routerLink] directive
    imports: [CommonModule, FormsModule, HttpClientModule, RouterModule], 
    templateUrl: './login.html',
    styleUrls: ['./login.css']
})
export class LoginComponent implements OnInit {

    loginData = { username: '', password: '' };
    errorMessage: string = '';
    loading: boolean = false;
    // NOTE: Keep 'http://127.0.0.1:5000/api/login' but remember 'localhost' is often more robust.
    private apiUrl = 'http://127.0.0.1:5000/api/login'; 

    constructor(
        private location: Location, 
        private http: HttpClient,
        private router: Router,
        private popupService: PopupService
    ) {}

    ngOnInit(): void { }

    onLoginSubmit(): void {
        this.errorMessage = '';
        
        if (!this.loginData.username || !this.loginData.password) {
            this.errorMessage = 'Username and password are required.';
            return;
        }

        this.loading = true;

        this.http.post<LoginResponse>(this.apiUrl, this.loginData)
            .subscribe({
                next: (response) => {
                    this.loading = false;
                    console.log('Login Successful:', response);
                    
                    // SUCCESS: Store user data and redirect
                    localStorage.setItem('current_user', JSON.stringify(response.user));
                    this.popupService.show(response.message);
                    this.router.navigate(['/topic-selection']);
                },
                error: (err) => {
                    this.loading = false;
                    // Display the custom error message from Flask or a generic message
                    this.errorMessage = err.error?.message || 'Login failed. An unknown error occurred.';
                    this.popupService.show(this.errorMessage, true);
                    console.error('Login Error:', err);
                }
            });
    }

    goBack(): void {
        this.location.back();
    }
}