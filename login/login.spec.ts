// import { ComponentFixture, TestBed } from '@angular/core/testing';

// import { Login } from './login';

// describe('Login', () => {
//   let component: Login;
//   let fixture: ComponentFixture<Login>;

//   beforeEach(async () => {
//     await TestBed.configureTestingModule({
//       imports: [Login]
//     })
//     .compileComponents();

//     fixture = TestBed.createComponent(Login);
//     component = fixture.componentInstance;
//     fixture.detectChanges();
//   });

//   it('should create', () => {
//     expect(component).toBeTruthy();
//   });
// });
import { ComponentFixture, TestBed } from '@angular/core/testing';

// FIX: Import the component using the standard Angular class name.
import { LoginComponent } from './login'; 

// FIX: Change the describe block to use the correct class name for clarity.
describe('LoginComponent', () => { 
    // FIX: Use the correct component class type.
    let component: LoginComponent;
    let fixture: ComponentFixture<LoginComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            // FIX: Import the component using the correct class name.
            imports: [LoginComponent]
        })
        .compileComponents();

        // FIX: Create the component using the correct class name.
        fixture = TestBed.createComponent(LoginComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});