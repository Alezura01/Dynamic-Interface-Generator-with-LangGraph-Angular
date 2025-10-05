import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MatInputComponent } from './mat-input.component';

describe('MatInputComponent', () => {
  let component: MatInputComponent;
  let fixture: ComponentFixture<MatInputComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatInputComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MatInputComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
