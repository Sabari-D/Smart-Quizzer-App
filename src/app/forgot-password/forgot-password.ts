// import { Component, OnInit } from '@angular/core';
// import { Location, CommonModule } from '@angular/common';
// import { FormsModule } from '@angular/forms';
// import { HttpClient, HttpClientModule } from '@angular/common/http';
// import { Router, RouterModule } from '@angular/router';

// @Component({
//   selector: 'app-forgot-password',
//   standalone: true,
//   imports: [CommonModule, FormsModule, HttpClientModule, RouterModule],
//   templateUrl: './forgot-password.html',
//   styleUrls: ['./forgot-password.css']
// })
// export class ForgotPasswordComponent implements OnInit {
  
//   usernameOrEmail: string = '';
//   message: string = '';
//   errorMessage: string = '';
//   loading: boolean = false;

//   private apiUrl = 'http://127.0.0.1:5000/api/forgot_password'; 

//   constructor(
//     private location: Location, 
//     private http: HttpClient,
//     private router: Router
//   ) {}

//   ngOnInit(): void {
//     // Initialization
//   }
  
//   /**
//    * Sends the username/email to the backend to generate a reset token.
//    */
//   onRequestReset(): void {
//     this.message = '';
//     this.errorMessage = '';

//     if (!this.usernameOrEmail) {
//       this.errorMessage = 'Please enter your username or email.';
//       return;
//     }

//     this.loading = true;

//     // Send only the identifier to the Flask server
//     this.http.post<any>(this.apiUrl, { identifier: this.usernameOrEmail })
//       .subscribe({
//         next: (response) => {
//           this.loading = false;
//           // IMPORTANT: Display the success message, even if simplified (e.g., "Check console for token")
//           this.message = response.message || 'If an account exists, a reset link has been processed.';
          
//           // Optional: Redirect to a confirmation page
//           // this.router.navigate(['/login']); 
//         },
//         error: (err) => {
//           this.loading = false;
//           // For security, we often show a generic success message even on error
//           this.message = 'If an account exists, a reset link has been processed.';
//           console.error('Reset Request Error:', err);
//         }
//       });
//   }

//   goBack(): void {
//     this.location.back();
//   }
// }




// import { Component, OnInit } from '@angular/core';
// import { Location, CommonModule } from '@angular/common';
// import { FormsModule } from '@angular/forms';
// import { HttpClient, HttpClientModule } from '@angular/common/http';
// import { Router, RouterModule } from '@angular/router';

// @Component({
//   selector: 'app-forgot-password',
//   standalone: true,
//   imports: [CommonModule, FormsModule, HttpClientModule, RouterModule],
//   templateUrl: './forgot-password.html',
//   styleUrls: ['./forgot-password.css']
// })
// export class ForgotPasswordComponent implements OnInit {
  
//   identifier: string = '';
//   resetMethod: 'email' | 'mobile' = 'email';
  
//   // OTP verification (for mobile)
//   showOtpInput: boolean = false;
//   otpCode: string = '';
  
//   message: string = '';
//   errorMessage: string = '';
//   loading: boolean = false;
//   success: boolean = false;
  
//   // For OTP resend
//   canResendOtp: boolean = false;
//   resendTimer: number = 60;
//   private resendInterval: any;

//   private apiUrl = 'http://127.0.0.1:5000/api/forgot_password';
//   private verifyOtpUrl = 'http://127.0.0.1:5000/api/verify_otp';

//   constructor(
//     private location: Location, 
//     private http: HttpClient,
//     private router: Router
//   ) {}

//   ngOnInit(): void {
//     // Initialization
//   }

//   ngOnDestroy(): void {
//     if (this.resendInterval) {
//       clearInterval(this.resendInterval);
//     }
//   }
  
//   /**
//    * Detect if input is email or mobile and set method accordingly
//    */
//   onIdentifierChange(): void {
//     if (this.identifier.includes('@')) {
//       this.resetMethod = 'email';
//     } else if (this.identifier.match(/^\d{10}$/)) {
//       this.resetMethod = 'mobile';
//     }
//   }

//   /**
//    * Validate identifier based on type
//    */
//   validateIdentifier(): string | null {
//     if (!this.identifier.trim()) {
//       return 'Please enter your email or mobile number.';
//     }

//     if (this.identifier.includes('@')) {
//       const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
//       if (!emailRegex.test(this.identifier)) {
//         return 'Please enter a valid email address.';
//       }
//     } else {
//       const mobileRegex = /^[6-9]\d{9}$/;
//       if (!mobileRegex.test(this.identifier)) {
//         return 'Please enter a valid 10-digit mobile number.';
//       }
//     }

//     return null;
//   }

//   /**
//    * Request password reset (email link or mobile OTP)
//    */
//   onRequestReset(): void {
//     this.message = '';
//     this.errorMessage = '';
//     this.success = false;

//     const validationError = this.validateIdentifier();
//     if (validationError) {
//       this.errorMessage = validationError;
//       return;
//     }

//     this.loading = true;

//     const payload = {
//       identifier: this.identifier,
//       method: this.resetMethod
//     };

//     this.http.post<any>(this.apiUrl, payload)
//       .subscribe({
//         next: (response) => {
//           this.loading = false;
//           if (response.success) {
//             this.success = true;
//             this.message = response.message;
            
//             // If mobile method, show OTP input
//             if (response.method === 'mobile') {
//               this.showOtpInput = true;
//               this.startResendTimer();
//             } else {
//               // For email, redirect to login after 5 seconds
//               setTimeout(() => {
//                 this.router.navigate(['/login']);
//               }, 5000);
//             }
//           } else {
//             this.errorMessage = response.message || 'An error occurred. Please try again.';
//           }
//         },
//         error: (err) => {
//           this.loading = false;
//           // Generic message for security
//           this.errorMessage = 'An error occurred. Please try again or check your connection.';
//           console.error('Reset Request Error:', err);
//         }
//       });
//   }

//   /**
//    * Verify OTP for mobile-based reset
//    */
//   onVerifyOtp(): void {
//     this.message = '';
//     this.errorMessage = '';

//     if (!this.otpCode || this.otpCode.length !== 6) {
//       this.errorMessage = 'Please enter a valid 6-digit OTP.';
//       return;
//     }

//     this.loading = true;

//     const payload = {
//       mobile: this.identifier,
//       otp: this.otpCode
//     };

//     this.http.post<any>(this.verifyOtpUrl, payload)
//       .subscribe({
//         next: (response) => {
//           this.loading = false;
//           if (response.success) {
//             this.success = true;
//             this.message = 'OTP verified! Redirecting to reset password...';
            
//             // Navigate to reset password page with token
//             setTimeout(() => {
//               this.router.navigate(['/reset-password'], {
//                 queryParams: {
//                   token: response.reset_token,
//                   type: 'mobile'
//                 }
//               });
//             }, 1500);
//           } else {
//             this.errorMessage = response.message || 'Invalid OTP. Please try again.';
//           }
//         },
//         error: (err) => {
//           this.loading = false;
//           this.errorMessage = err.error?.message || 'OTP verification failed. Please try again.';
//           console.error('OTP Verification Error:', err);
//         }
//       });
//   }

//   /**
//    * Start countdown timer for OTP resend
//    */
//   startResendTimer(): void {
//     this.canResendOtp = false;
//     this.resendTimer = 60;
    
//     this.resendInterval = setInterval(() => {
//       this.resendTimer--;
//       if (this.resendTimer <= 0) {
//         this.canResendOtp = true;
//         clearInterval(this.resendInterval);
//       }
//     }, 1000);
//   }

//   /**
//    * Resend OTP
//    */
//   onResendOtp(): void {
//     if (!this.canResendOtp) return;
    
//     this.otpCode = '';
//     this.message = '';
//     this.errorMessage = '';
//     this.onRequestReset();
//   }

//   /**
//    * Switch between email and mobile methods
//    */
//   switchMethod(): void {
//     this.identifier = '';
//     this.showOtpInput = false;
//     this.otpCode = '';
//     this.message = '';
//     this.errorMessage = '';
//     this.resetMethod = this.resetMethod === 'email' ? 'mobile' : 'email';
//   }

//   goBack(): void {
//     this.location.back();
//   }

//   goToLogin(): void {
//     this.router.navigate(['/login']);
//   }
// }







// import { Component, OnInit, OnDestroy } from '@angular/core';
// import { Location, CommonModule } from '@angular/common';
// import { FormsModule } from '@angular/forms';
// import { HttpClient, HttpClientModule } from '@angular/common/http';
// import { Router, RouterModule } from '@angular/router';

// @Component({  
//   selector: 'app-forgot-password',
//   standalone: true,
//   imports: [CommonModule, FormsModule, HttpClientModule, RouterModule],
//   templateUrl: './forgot-password.html',
//   styleUrls: ['./forgot-password.css']
// })
// export class ForgotPasswordComponent implements OnInit, OnDestroy {
  
//   identifier: string = '';
//   resetMethod: 'email' | 'mobile' = 'email';
  
//   // OTP verification (for mobile)
//   showOtpInput: boolean = false;
//   otpCode: string = '';
  
//   message: string = '';
//   errorMessage: string = '';
//   loading: boolean = false;
//   success: boolean = false;
  
//   // For OTP resend
//   canResendOtp: boolean = false;
//   resendTimer: number = 60;
//   private resendInterval: any;

//   private apiUrl = 'http://127.0.0.1:5000/api/forgot_password';
//   private verifyOtpUrl = 'http://127.0.0.1:5000/api/verify_otp';

//   constructor(
//     private location: Location, 
//     private http: HttpClient,
//     private router: Router
//   ) {}

//   ngOnInit(): void {
//     // Initialization
//   }

//   ngOnDestroy(): void {
//     if (this.resendInterval) {
//       clearInterval(this.resendInterval);
//     }
//   }
  
//   /**
//    * Detect if input is email or mobile and set method accordingly
//    */
//   onIdentifierChange(): void {
//     if (this.identifier.includes('@')) {
//       this.resetMethod = 'email';
//     } else if (this.identifier.match(/^\d{10}$/)) {
//       this.resetMethod = 'mobile';
//     }
//   }

//   /**
//    * Validate identifier based on type
//    */
//   validateIdentifier(): string | null {
//     if (!this.identifier.trim()) {
//       return 'Please enter your email or mobile number.';
//     }

//     if (this.identifier.includes('@')) {
//       const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
//       if (!emailRegex.test(this.identifier)) {
//         return 'Please enter a valid email address.';
//       }
//     } else {
//       const mobileRegex = /^[6-9]\d{9}$/;
//       if (!mobileRegex.test(this.identifier)) {
//         return 'Please enter a valid 10-digit mobile number.';
//       }
//     }

//     return null;
//   }

//   /**
//    * Request password reset (email link or mobile OTP)
//    */
//   onRequestReset(): void {
//     this.message = '';
//     this.errorMessage = '';
//     this.success = false;

//     const validationError = this.validateIdentifier();
//     if (validationError) {
//       this.errorMessage = validationError;
//       return;
//     }

//     this.loading = true;

//     const payload = {
//       identifier: this.identifier,
//       method: this.resetMethod
//     };

//     this.http.post<any>(this.apiUrl, payload)
//       .subscribe({
//         next: (response) => {
//           this.loading = false;
          
//           // --- INTEGRATING THE REQUESTED CONSOLE LOG DISPLAY FEATURE ---
//           if (this.resetMethod === 'email' && response.reset_token_hash) {
//             // NOTE: Flask is returning the raw token in the hash field during testing
//             const resetLink = `http://localhost:4200/reset-password?token=${response.reset_token}&type=email`;
            
//             // Display the full link in the success message for copying (developer testing)
//             this.message = `Verification successful. COPY THIS LINK: ${resetLink}`;
//           } else {
//              // For OTP or production email, use the message from the backend
//              this.message = response.message || 'If an account exists, a reset link has been processed.';
//           }
//           // --- END INTEGRATION ---

//           if (response.success) {
//             this.success = true;
            
//             // If mobile method, show OTP input
//             if (response.method === 'mobile') {
//               this.showOtpInput = true;
//               this.startResendTimer();
//             } else {
//               // For email, redirect to login after 5 seconds
//               setTimeout(() => {
//                 this.router.navigate(['/login']);
//               }, 5000);
//             }
//           } else {
//             this.errorMessage = response.message || 'An error occurred. Please try again.';
//           }
//         },
//         error: (err) => {
//           this.loading = false;
//           this.errorMessage = 'An error occurred. Please try again or check your connection.';
//           console.error('Reset Request Error:', err);
//         }
//       });
//   }

//   /**
//    * Verify OTP for mobile-based reset
//    */
//   onVerifyOtp(): void {
//     this.message = '';
//     this.errorMessage = '';

//     if (!this.otpCode || this.otpCode.length !== 6) {
//       this.errorMessage = 'Please enter a valid 6-digit OTP.';
//       return;
//     }

//     this.loading = true;

//     const payload = {
//       mobile: this.identifier,
//       otp: this.otpCode
//     };

//     this.http.post<any>(this.verifyOtpUrl, payload)
//       .subscribe({
//         next: (response) => {
//           this.loading = false;
//           if (response.success) {
//             this.success = true;
//             this.message = 'OTP verified! Redirecting to reset password...';
            
//             // Navigate to reset password page with token
//             setTimeout(() => {
//               this.router.navigate(['/reset-password'], {
//                 queryParams: {
//                   token: response.reset_token,
//                   type: 'mobile'
//                 }
//               });
//             }, 1500);
//           } else {
//             this.errorMessage = response.message || 'Invalid OTP. Please try again.';
//           }
//         },
//         error: (err) => {
//           this.loading = false;
//           this.errorMessage = err.error?.message || 'OTP verification failed. Please try again.';
//           console.error('OTP Verification Error:', err);
//         }
//       });
//   }

//   /**
//    * Start countdown timer for OTP resend
//    */
//   startResendTimer(): void {
//     this.canResendOtp = false;
//     this.resendTimer = 60;
    
//     this.resendInterval = setInterval(() => {
//       this.resendTimer--;
//       if (this.resendTimer <= 0) {
//         this.canResendOtp = true;
//         clearInterval(this.resendInterval);
//       }
//     }, 1000);
//   }

//   /**
//    * Resend OTP
//    */
//   onResendOtp(): void {
//     if (!this.canResendOtp) return;
    
//     this.otpCode = '';
//     this.message = '';
//     this.errorMessage = '';
    
//     if (this.resendInterval) {
//         clearInterval(this.resendInterval);
//     }
    
//     this.onRequestReset();
//   }

//   /**
//    * Switch between email and mobile methods
//    */
//   switchMethod(): void {
//     this.identifier = '';
//     this.showOtpInput = false;
//     this.otpCode = '';
//     this.message = '';
//     this.errorMessage = '';
//     this.resetMethod = this.resetMethod === 'email' ? 'mobile' : 'email';
//   }

//   goBack(): void {
//     this.location.back();
//   }

//   goToLogin(): void {
//     this.router.navigate(['/login']);
//   }
// }





// import { Component, OnInit, OnDestroy, Inject, PLATFORM_ID } from '@angular/core';
// import { Location, CommonModule, isPlatformBrowser } from '@angular/common';
// import { FormsModule } from '@angular/forms';
// import { HttpClient, HttpClientModule } from '@angular/common/http';
// import { Router, RouterModule } from '@angular/router';

// @Component({
//   selector: 'app-forgot-password',
//   standalone: true,
//   imports: [CommonModule, FormsModule, HttpClientModule, RouterModule],
//   templateUrl: './forgot-password.html',
//   styleUrls: ['./forgot-password.css']
// })
// export class ForgotPasswordComponent implements OnInit, OnDestroy {
  
//   identifier: string = '';
//   resetMethod: 'email' | 'mobile' = 'email';
  
//   // OTP verification (for mobile)
//   showOtpInput: boolean = false;
//   otpCode: string = '';
  
//   message: string = '';
//   errorMessage: string = '';
//   loading: boolean = false;
//   success: boolean = false;

//   // FIX: Added the property to hold the link for display
//   resetLinkDisplayed: string | null = null; 
  
//   // For OTP resend
//   canResendOtp: boolean = false;
//   resendTimer: number = 60;
//   private resendInterval: any;

//   private apiUrl = 'http://127.0.0.1:5000/api/forgot_password';
//   private verifyOtpUrl = 'http://127.0.0.1:5000/api/verify_otp';

//   constructor(
//     private location: Location, 
//     private http: HttpClient,
//     private router: Router
//     // Note: PLATFORM_ID injection omitted here for simplicity, assuming environment runs safely
//   ) {}

//   ngOnInit(): void {
//     // Initialization
//   }

//   ngOnDestroy(): void {
//     if (this.resendInterval) {
//       clearInterval(this.resendInterval);
//     }
//   }
  
//   /**
//    * Detect if input is email or mobile and set method accordingly
//    */
//   onIdentifierChange(): void {
//     if (this.identifier.includes('@')) {
//       this.resetMethod = 'email';
//     } else if (this.identifier.match(/^\d{10}$/)) {
//       this.resetMethod = 'mobile';
//     }
//     this.resetLinkDisplayed = null; // Clear displayed link on identifier change
//   }

//   /**
//    * Validate identifier based on type
//    */
//   validateIdentifier(): string | null {
//     if (!this.identifier.trim()) {
//       return 'Please enter your email or mobile number.';
//     }

//     if (this.identifier.includes('@')) {
//       const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
//       if (!emailRegex.test(this.identifier)) {
//         return 'Please enter a valid email address.';
//       }
//     } else {
//       const mobileRegex = /^[6-9]\d{9}$/;
//       if (!mobileRegex.test(this.identifier)) {
//         return 'Please enter a valid 10-digit mobile number.';
//       }
//     }
//     return null;
//   }

//   /**
//    * Request password reset (email link or mobile OTP)
//    */
//   onRequestReset(): void {
//     this.message = '';
//     this.errorMessage = '';
//     this.success = false;
//     this.resetLinkDisplayed = null; // Clear previous link

//     const validationError = this.validateIdentifier();
//     if (validationError) {
//       this.errorMessage = validationError;
//       return;
//     }

//     this.loading = true;

//     const payload = {
//       identifier: this.identifier,
//       method: this.resetMethod
//     };

//     this.http.post<any>(this.apiUrl, payload)
//       .subscribe({
//         next: (response) => {
//           this.loading = false;
          
//           if (response.success) {
//             this.success = true;
//             this.message = response.message;

//             // --- CRITICAL INTEGRATION: DISPLAY LINK FOR EMAIL METHOD ---
//             if (response.method === 'email' && response.reset_token) {
//                 const resetLink = `http://localhost:4200/reset-password?token=${response.reset_token}&type=email`;
                
//                 // Display the full link in the message property for copying
//                 this.message = `Verification successful. COPY THIS LINK: ${resetLink}`;
//                 this.resetLinkDisplayed = resetLink; // Store the link for the copy button
                
//                 // Redirect is not needed here; the link is displayed for manual copy/use
//             } 
//             // --- END INTEGRATION ---

//             // If mobile method, show OTP input
//             if (response.method === 'mobile') {
//               this.showOtpInput = true;
//               this.startResendTimer();
//             } 
            
//           } else {
//             this.errorMessage = response.message || 'An error occurred. Please try again.';
//           }
//         },
//         error: (err) => {
//           this.loading = false;
//           this.errorMessage = 'An error occurred. Please try again or check your connection.';
//           console.error('Reset Request Error:', err);
//         }
//       });
//   }

//   /**
//    * Verify OTP for mobile-based reset
//    */
//   onVerifyOtp(): void {
//     this.message = '';
//     this.errorMessage = '';

//     if (!this.otpCode || this.otpCode.length !== 6) {
//       this.errorMessage = 'Please enter a valid 6-digit OTP.';
//       return;
//     }

//     this.loading = true;

//     const payload = {
//       mobile: this.identifier,
//       otp: this.otpCode
//     };

//     this.http.post<any>(this.verifyOtpUrl, payload)
//       .subscribe({
//         next: (response) => {
//           this.loading = false;
//           if (response.success) {
//             this.success = true;
//             this.message = 'OTP verified! Redirecting to reset password...';
            
//             // Navigate to reset password page with token
//             setTimeout(() => {
//               this.router.navigate(['/reset-password'], {
//                 queryParams: {
//                   token: response.reset_token,
//                   type: 'mobile'
//                 }
//               });
//             }, 1500);
//           } else {
//             this.errorMessage = response.message || 'Invalid OTP. Please try again.';
//           }
//         },
//         error: (err) => {
//           this.loading = false;
//           this.errorMessage = err.error?.message || 'OTP verification failed. Please try again.';
//           console.error('OTP Verification Error:', err);
//         }
//       });
//   }

//   /**
//    * Start countdown timer for OTP resend
//    */
//   startResendTimer(): void {
//     this.canResendOtp = false;
//     this.resendTimer = 60;
    
//     this.resendInterval = setInterval(() => {
//       this.resendTimer--;
//       if (this.resendTimer <= 0) {
//         this.canResendOtp = true;
//         clearInterval(this.resendInterval);
//       }
//     }, 1000);
//   }

//   /**
//    * Resend OTP
//    */
//   onResendOtp(): void {
//     if (!this.canResendOtp) return;
    
//     this.otpCode = '';
//     this.message = '';
//     this.errorMessage = '';
//     this.resetLinkDisplayed = null; // Clear link if resending
    
//     if (this.resendInterval) {
//         clearInterval(this.resendInterval);
//     }
    
//     this.onRequestReset();
//   }

//   /**
//    * Switch between email and mobile methods
//    */
//   switchMethod(): void {
//     this.identifier = '';
//     this.showOtpInput = false;
//     this.otpCode = '';
//     this.message = '';
//     this.errorMessage = '';
//     this.resetLinkDisplayed = null; // Clear link on method switch
//     this.resetMethod = this.resetMethod === 'email' ? 'mobile' : 'email';
//   }

//   /**
//    * Standard Navigation Functions
//    */
//   goBack(): void {
//     this.location.back();
//   }

//   goToLogin(): void {
//     this.router.navigate(['/login']);
//   }
// } 



import { Component, OnInit, OnDestroy, Inject, PLATFORM_ID } from '@angular/core'; 
import { Location, CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule, RouterModule],
  templateUrl: './forgot-password.html',
  styleUrls: ['./forgot-password.css']
})
export class ForgotPasswordComponent implements OnInit, OnDestroy {
  
  identifier: string = '';
  resetMethod: 'email' | 'mobile' = 'email';
  
  // OTP verification (for mobile)
  showOtpInput: boolean = false;
  otpCode: string = '';
  
  message: string = '';
  errorMessage: string = '';
  loading: boolean = false;
  success: boolean = false;

  // Property to hold the link for display
  resetLinkDisplayed: string | null = null; 
  
  // For OTP resend
  canResendOtp: boolean = false;
  resendTimer: number = 60;
  private resendInterval: any;

  private apiUrl = 'http://127.0.0.1:5000/api/forgot_password';
  private verifyOtpUrl = 'http://127.0.0.1:5000/api/verify_otp';

  constructor(
    private location: Location, 
    private http: HttpClient,
    private router: Router
    // PLATFORM_ID is technically needed for copyLink, but omitted as per your original file structure
  ) {}

  ngOnInit(): void {
    // Initialization
  }

  ngOnDestroy(): void {
    if (this.resendInterval) {
      clearInterval(this.resendInterval);
    }
  }
  
  /**
   * Detect if input is email or mobile and set method accordingly
   */
  onIdentifierChange(): void {
    if (this.identifier.includes('@')) {
      this.resetMethod = 'email';
    } else if (this.identifier.match(/^\d{10}$/)) {
      this.resetMethod = 'mobile';
    }
    this.resetLinkDisplayed = null; // Clear displayed link on identifier change
  }

  /**
   * Validate identifier based on type
   */
  validateIdentifier(): string | null {
    if (!this.identifier.trim()) {
      return 'Please enter your email or mobile number.';
    }

    if (this.identifier.includes('@')) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(this.identifier)) {
        return 'Please enter a valid email address.';
      }
    } else {
      const mobileRegex = /^[6-9]\d{9}$/;
      if (!mobileRegex.test(this.identifier)) {
        return 'Please enter a valid 10-digit mobile number.';
      }
    }
    return null;
  }

  /**
   * Request password reset (email link or mobile OTP)
   */
  onRequestReset(): void {
    this.message = '';
    this.errorMessage = '';
    this.success = false;
    this.resetLinkDisplayed = null; // Clear previous link

    const validationError = this.validateIdentifier();
    if (validationError) {
      this.errorMessage = validationError;
      return;
    }

    this.loading = true;

    const payload = {
      identifier: this.identifier,
      method: this.resetMethod
    };

    this.http.post<any>(this.apiUrl, payload)
      .subscribe({
        next: (response) => {
          this.loading = false;
          
          if (response.success) {
            this.success = true;
            this.message = response.message;

            // --- CRITICAL INTEGRATION: DISPLAY LINK AND TOKEN ---
            if (this.resetMethod === 'email' && response.reset_token) {
                const frontendUrl = 'http://localhost:4200';
                this.resetLinkDisplayed = `${frontendUrl}/reset-password?token=${response.reset_token}&type=email`;
                // Override message to prompt user to copy the link
                this.message = 'Verification successful. COPY THIS LINK:';
            } 
            // --- END INTEGRATION ---

            // If mobile method, show OTP input
            if (response.method === 'mobile') {
              // Assume PLATFORM_ID check passed and sessionStorage is available
              sessionStorage.setItem('reset_identifier', this.identifier);
              this.showOtpInput = true;
              this.startResendTimer();
            } else if (response.method === 'email' && !response.reset_token) {
              // Fallback for generic email success message (in production, redirect)
              setTimeout(() => {
                this.router.navigate(['/login']);
              }, 5000);
            }
            
          } else {
            this.errorMessage = response.message || 'An error occurred. Please try again.';
          }
        },
        error: (err) => {
          this.loading = false;
          this.errorMessage = 'An error occurred. Please try again or check your connection.';
          console.error('Reset Request Error:', err);
        }
      });
  }

  /**
   * Verify OTP for mobile-based reset
   */
  onVerifyOtp(): void {
    this.message = '';
    this.errorMessage = '';

    if (!this.otpCode || this.otpCode.length !== 6) {
      this.errorMessage = 'Please enter a valid 6-digit OTP.';
      return;
    }

    this.loading = true;

    const payload = {
      mobile: this.identifier,
      otp: this.otpCode
    };

    this.http.post<any>(this.verifyOtpUrl, payload)
      .subscribe({
        next: (response) => {
          this.loading = false;
          if (response.success) {
            this.success = true;
            this.message = 'OTP verified! Redirecting to reset password...';
            
            // Navigate to reset password page with token
            setTimeout(() => {
              this.router.navigate(['/reset-password'], {
                queryParams: {
                  token: response.reset_token,
                  type: 'mobile'
                }
              });
            }, 1500);
          } else {
            this.errorMessage = response.message || 'Invalid OTP. Please try again.';
          }
        },
        error: (err) => {
          this.loading = false;
          this.errorMessage = err.error?.message || 'OTP verification failed. Please try again.';
          console.error('OTP Verification Error:', err);
        }
      });
  }

  /**
   * Start countdown timer for OTP resend
   */
  startResendTimer(): void {
    this.canResendOtp = false;
    this.resendTimer = 60;
    
    this.resendInterval = setInterval(() => {
      this.resendTimer--;
      if (this.resendTimer <= 0) {
        this.canResendOtp = true;
        clearInterval(this.resendInterval);
      }
    }, 1000);
  }

  /**
   * Resend OTP
   */
  onResendOtp(): void {
    if (!this.canResendOtp) return;
    
    this.otpCode = '';
    this.message = '';
    this.errorMessage = '';
    this.resetLinkDisplayed = null; // Clear link if resending
    
    if (this.resendInterval) {
        clearInterval(this.resendInterval);
    }
    
    this.onRequestReset();
  }

  /**
   * Switch between email and mobile methods
   */
  switchMethod(): void {
    this.identifier = '';
    this.showOtpInput = false;
    this.otpCode = '';
    this.message = '';
    this.errorMessage = '';
    this.resetLinkDisplayed = null; // Clear link on method switch
    this.resetMethod = this.resetMethod === 'email' ? 'mobile' : 'email';
  }
  
  /**
   * Missing function for Copy Button in HTML
   */
  copyResetLink(): void {
    // Check if clipboard API is available (it should be in a modern browser)
    if (this.resetLinkDisplayed && typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(this.resetLinkDisplayed).then(() => {
        // Provide user feedback that the copy succeeded
        this.message = 'Link successfully copied to clipboard!';
      }).catch(err => {
        console.error('Failed to copy link: ', err);
        this.errorMessage = 'Failed to copy link. Please copy it manually.';
      });
    } else {
        // Fallback for non-browser environment or missing link
        this.errorMessage = 'Cannot copy link. Link not generated or clipboard unavailable.';
    }
  }

  /**
   * Standard Navigation Functions
   */
  goBack(): void {
    this.location.back();
  }

  goToLogin(): void {
    this.router.navigate(['/login']);
  }
}