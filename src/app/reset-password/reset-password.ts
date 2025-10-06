// import { Component, OnInit } from '@angular/core';
// import { CommonModule } from '@angular/common';
// import { FormsModule } from '@angular/forms';
// import { HttpClient, HttpClientModule } from '@angular/common/http';
// import { ActivatedRoute, Router } from '@angular/router';

// @Component({
//   selector: 'app-reset-password',
//   standalone: true,
//   imports: [CommonModule, FormsModule, HttpClientModule],
//   templateUrl: './reset-password.html',
//   styleUrls: ['./reset-password.css']
// })
// export class ResetPasswordComponent implements OnInit {
  
//   resetToken: string = '';
//   newPassword1: string = '';
//   newPassword2: string = '';

//   message: string = '';
//   errorMessage: string = '';
//   loading: boolean = false;
  
//   private apiUrl = 'http://127.0.0.1:5000/api/reset_password';

//   constructor(
//     private route: ActivatedRoute,
//     private router: Router,
//     private http: HttpClient
//   ) {}

//   ngOnInit(): void {
//     // Read the token from the URL (e.g., /reset-password?token=XYZ)
//     this.route.queryParams.subscribe(params => {
//       this.resetToken = params['token'] || '';
//       if (!this.resetToken) {
//         this.errorMessage = 'No valid reset token found in URL.';
//       }
//     });
//   }

//   /**
//    * Submits the new password along with the verified token to the backend.
//    */
//   onPasswordReset(): void {
//     this.message = '';
//     this.errorMessage = '';

//     if (!this.resetToken) {
//       this.errorMessage = 'Reset failed: Missing token.';
//       return;
//     }
//     if (this.newPassword1 !== this.newPassword2) {
//       this.errorMessage = 'New passwords do not match.';
//       return;
//     }
//     if (this.newPassword1.length < 6) {
//       this.errorMessage = 'Password must be at least 6 characters long.';
//       return;
//     }

//     this.loading = true;

//     const payload = {
//       token: this.resetToken,
//       new_password: this.newPassword1
//     };

//     this.http.post<any>(this.apiUrl, payload)
//       .subscribe({
//         next: (response) => {
//           this.loading = false;
//           this.message = response.message || 'Password updated successfully!';
//           // Redirect user to login after success
//           setTimeout(() => {
//             this.router.navigate(['/login']);
//           }, 3000);
//         },
//         error: (err) => {
//           this.loading = false;
//           // Display the specific error from Flask (Invalid/Expired token)
//           this.errorMessage = err.error?.message || 'Password reset failed.';
//           console.error('Reset Error:', err);
//         }
//       });
//   }
// }


// File: src/app/reset-password/reset-password.ts
// import { Component, OnInit } from '@angular/core';
// import { CommonModule } from '@angular/common';
// import { FormsModule } from '@angular/forms';
// import { HttpClient, HttpClientModule } from '@angular/common/http';
// import { ActivatedRoute, Router, RouterModule } from '@angular/router';

// @Component({
//   selector: 'app-reset-password',
//   standalone: true,
//   // Add necessary modules
//   imports: [CommonModule, FormsModule, HttpClientModule, RouterModule], 
//   templateUrl: './reset-password.html',
//   styleUrls: ['./reset-password.css']
// })
// export class ResetPasswordComponent implements OnInit {
  
//   resetToken: string = '';
//   newPassword1: string = '';
//   newPassword2: string = '';

//   message: string = '';
//   errorMessage: string = '';
//   loading: boolean = false;
  
//   // Use the API URL defined in your backend
//   private apiUrl = 'http://localhost:5000/api/reset_password'; 

//   constructor(
//     private route: ActivatedRoute, // To read the token from the URL
//     private router: Router,
//     private http: HttpClient
//   ) {}

//   ngOnInit(): void {
//     // CRITICAL: Read the token from the query parameters (e.g., ?token=XYZ)
//     this.route.queryParams.subscribe(params => {
//       this.resetToken = params['token'] || '';
//       if (!this.resetToken) {
//         this.errorMessage = 'No valid reset token found in URL. Please request a new link.';
//       }
//     });
//   }

//   onPasswordReset(): void {
//     this.message = '';
//     this.errorMessage = '';

//     if (!this.resetToken) {
//       this.errorMessage = 'Reset failed: Missing token.';
//       return;
//     }
//     if (this.newPassword1 !== this.newPassword2) {
//       this.errorMessage = 'New passwords do not match.';
//       return;
//     }
//     if (this.newPassword1.length < 6) {
//       this.errorMessage = 'Password must be at least 6 characters long.';
//       return;
//     }

//     this.loading = true;

//     const payload = {
//       token: this.resetToken,
//       new_password: this.newPassword1 // Sending the new password
//     };

//     // Send token and new password to Flask
//     this.http.post<any>(this.apiUrl, payload)
//       .subscribe({
//         next: (response) => {
//           this.loading = false;
//           this.message = response.message || 'Password updated successfully!';
//           // Redirect user to login after success
//           setTimeout(() => {
//             this.router.navigate(['/login']);
//           }, 3000);
//         },
//         error: (err) => {
//           this.loading = false;
//           // Display the specific error from Flask (Invalid/Expired token)
//           this.errorMessage = err.error?.message || 'Password reset failed.';
//           console.error('Reset Error:', err);
//         }
//       });
//   }
// }


import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule, RouterModule], 
  templateUrl: './reset-password.html',
  styleUrls: ['./reset-password.css']
})
export class ResetPasswordComponent implements OnInit {
  
  resetToken: string = '';
  resetType: 'email' | 'mobile' = 'email';
  newPassword1: string = '';
  newPassword2: string = '';

  message: string = '';
  errorMessage: string = '';
  loading: boolean = false;
  success: boolean = false;
  
  // Password visibility toggle (retained for good UX)
  showPassword1: boolean = false;
  showPassword2: boolean = false;
  
  // Password strength indicators model (retained for visual feedback, but its check is removed below)
  passwordStrength: {
    length: boolean;
    uppercase: boolean;
    lowercase: boolean;
    number: boolean;
    special: boolean;
  } = {
    length: false,
    uppercase: false,
    lowercase: false,
    number: false,
    special: false
  };
  
  private apiUrl = 'http://localhost:5000/api/reset_password'; 

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    // Read the token and type from query parameters
    this.route.queryParams.subscribe(params => {
      this.resetToken = params['token'] || '';
      this.resetType = params['type'] || 'email';
      
      if (!this.resetToken) {
        this.errorMessage = 'No valid reset token found. Please request a new password reset.';
      }
    });
  }

  /**
   * Validate password strength in real-time (Kept for visual feedback)
   */
  validatePassword(): void {
    this.passwordStrength = {
      length: this.newPassword1.length >= 8,
      uppercase: /[A-Z]/.test(this.newPassword1),
      lowercase: /[a-z]/.test(this.newPassword1),
      number: /\d/.test(this.newPassword1),
      special: /[@$!%*?&]/.test(this.newPassword1)
    };
  }

  /**
   * Check if password meets all requirements (CRITICAL: Only used for UI feedback now)
   */
  isPasswordValid(): boolean {
    // This function is still used by the password strength bar visual, but not to block submission.
    return Object.values(this.passwordStrength).every(requirement => requirement);
  }

  // --- (togglePasswordVisibility and getPasswordStrengthLevel functions remain the same) ---
  togglePasswordVisibility(field: 1 | 2): void {
    if (field === 1) {
      this.showPassword1 = !this.showPassword1;
    } else {
      this.showPassword2 = !this.showPassword2;
    }
  }

  getPasswordStrengthLevel(): { level: string, color: string, width: string } {
    const validCount = Object.values(this.passwordStrength).filter(v => v).length;
    
    if (validCount === 0) {
      return { level: '', color: '', width: '0%' };
    } else if (validCount <= 2) {
      return { level: 'Weak', color: '#f44336', width: '33%' };
    } else if (validCount <= 4) {
      return { level: 'Medium', color: '#ff9800', width: '66%' };
    } else {
      return { level: 'Strong', color: '#4caf50', width: '100%' };
    }
  }


  /**
   * Reset password with new password (SUBMISSION LOGIC)
   */
  onPasswordReset(): void {
    this.message = '';
    this.errorMessage = '';
    this.success = false;

    if (!this.resetToken) {
      this.errorMessage = 'Reset failed: Missing token. Please request a new reset link.';
      return;
    }
    
    if (!this.newPassword1 || !this.newPassword2) {
      this.errorMessage = 'Please enter and confirm your new password.';
      return;
    }
    
    if (this.newPassword1 !== this.newPassword2) {
      this.errorMessage = 'Passwords do not match. Please try again.';
      return;
      // NOTE: We rely on the 6-character length check in Flask now!
    }
    
    // CRITICAL FIX: Removed the line below, which was blocking the submission:
    // if (!this.isPasswordValid()) { ... return; } 

    this.loading = true;

    const payload = {
      token: this.resetToken,
      new_password: this.newPassword1
    };

    this.http.post<any>(this.apiUrl, payload)
      .subscribe({
        next: (response) => {
          this.loading = false;
          if (response.success) {
            this.success = true;
            this.message = response.message;
            
            // Clear form and strength indicators
            this.newPassword1 = '';
            this.newPassword2 = '';
            this.validatePassword(); 
            
            // Redirect to login after success
            setTimeout(() => {
              this.router.navigate(['/login'], {
                queryParams: { resetSuccess: 'true' }
              });
            }, 3000);
          } else {
            // Failure from backend (e.g., token expired, token invalid, or password too short)
            this.errorMessage = response.message || 'Password reset failed. Please try again.';
          }
        },
        error: (err) => {
          this.loading = false;
          this.errorMessage = err.error?.message || 'Password reset failed. The link may have expired.';
          console.error('Reset Error:', err);
        }
      });
  }

  /**
   * Request a new reset link/OTP
   */
  requestNewLink(): void {
    this.router.navigate(['/forgot-password']);
  }
}