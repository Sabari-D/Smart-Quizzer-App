import { Component, OnInit } from '@angular/core';
import { Location, CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Router, RouterModule, ActivatedRoute } from '@angular/router';
import { Inject, PLATFORM_ID } from '@angular/core'; // For safe localStorage access

@Component({
  selector: 'app-verify-otp',
  // FIX: Ensure all imports are present for standalone component
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule, RouterModule], 
  templateUrl: './verify-otp.html', // Note: Using non-standard name for consistency
  styleUrls: ['./verify-otp.css']
})
export class VerifyOtpComponent implements OnInit {
  
  identifier: string = ''; // Username, email, or mobile number received from previous step
  otpCode: string = '';
  message: string = '';
  errorMessage: string = '';
  loading: boolean = false;

  private apiUrl = 'http://localhost:5000/api/verify_otp'; 
  
  constructor(
    private location: Location, 
    private http: HttpClient,
    private router: Router,
    private route: ActivatedRoute, // To read parameters if needed
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    // CRITICAL: Fetch the identifier (mobile/email) saved from the initial forgot-password request
    if (isPlatformBrowser(this.platformId)) {
      // Assuming you stored the identifier in session storage after the /forgot_password call
      const storedIdentifier = sessionStorage.getItem('reset_identifier');
      if (storedIdentifier) {
        this.identifier = storedIdentifier;
      } else {
        this.errorMessage = "Session expired or identifier missing. Please request a new reset.";
      }
    }
  }
  
  /**
   * Sends the 6-digit OTP code to the backend for verification.
   */
  onVerifyCode(): void {
    this.message = '';
    this.errorMessage = '';

    if (!this.otpCode || this.otpCode.length !== 6) {
      this.errorMessage = 'Please enter the 6-digit code.';
      return;
    }
    if (!this.identifier) {
       this.errorMessage = 'Cannot verify: Missing identifier.';
       return;
    }

    this.loading = true;

    const payload = {
      mobile: this.identifier, // Sending the identifier back to the server for lookup
      otp: this.otpCode
    };

    this.http.post<any>(this.apiUrl, payload)
      .subscribe({
        next: (response) => {
          this.loading = false;
          this.message = response.message;
          
          // CRITICAL STEP: If verification is successful, store the final reset token 
          // and redirect to the final password reset form.
          if (response.success && response.reset_token) {
            if (isPlatformBrowser(this.platformId)) {
                // Store the verification token temporarily for the final reset component
                sessionStorage.setItem('final_reset_token', response.reset_token);
            }
            
            // Redirect to the final password reset form
            this.router.navigate(['/reset-password']); 
          }
        },
        error: (err) => {
          this.loading = false;
          // Display the specific error from Flask (Invalid/Expired code)
          this.errorMessage = err.error?.message || 'Verification failed. Try requesting a new code.';
          console.error('OTP Verification Error:', err);
        }
      });
  }

  goBack(): void {
    this.location.back();
  }
}