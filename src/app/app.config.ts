// import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
// import { provideRouter } from '@angular/router';
// import { provideHttpClient } from '@angular/common/http'; // 1. Import HTTP provider
// import { FormsModule } from '@angular/forms'; // 2. Import FormsModule

// import { routes } from './app.routes';

// export const appConfig: ApplicationConfig = {
//   providers: [
//     provideZoneChangeDetection({ eventCoalescing: true }),
//     provideRouter(routes),
//     provideHttpClient(), // 3. Add the HTTP provider
//     // Note: FormsModule is imported differently in standalone components, see below
//   ]
// };

import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withFetch } from '@angular/common/http';
// FIX: Import the PopupService
import { PopupService } from './services/popup'; 
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    // HttpClient configuration is correct
    provideHttpClient(withFetch()), 
    
    // FIX: Provide the PopupService globally
    PopupService, 
  ]
};