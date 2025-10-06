import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PopupService {
  private popupSubject = new Subject<{ message: string, isError: boolean }>();
  popupState$ = this.popupSubject.asObservable();

  show(message: string, isError: boolean = false) {
    this.popupSubject.next({ message, isError });
  }
}