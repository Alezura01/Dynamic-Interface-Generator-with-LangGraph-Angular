import { Component, Output, Input, OnChanges, SimpleChange, SimpleChanges, signal, EventEmitter, ChangeDetectionStrategy } from '@angular/core';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule, FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {merge} from 'rxjs'

@Component({
  selector: 'app-mat-input',
  imports: [CommonModule, MatSelectModule, FormsModule, MatFormFieldModule, MatInputModule, MatIconModule, ReactiveFormsModule],
  templateUrl: './mat-input.component.html',
  styleUrl: './mat-input.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MatInputComponent implements OnChanges {
  @Input() inputDati: any[] = [];
  @Output() formDataChanged = new EventEmitter<{ [key: string]: string }>();
  @Output() inputCompilato = new EventEmitter<{id:string, valido:boolean}>();

  formData: { [key: string]: string} = {};
  labels: string[] = [];
  types: string[] = [];
  id: string[] = [];
  required: boolean[] = [];
  

  readonly email = new FormControl('', [Validators.required, Validators.email ]);
  errorMessage = signal('');

  constructor(){
    merge(this.email.statusChanges, this.email.valueChanges)
      .pipe(takeUntilDestroyed())
      .subscribe(()=> this.updateErrorMessage())
  }

  updateErrorMessage() {
    if(this.email.hasError('required')) {
      this.errorMessage.set('Devi inserire un valore');
    } else if (this.email.hasError('email')) {
      this.errorMessage.set('Email non valida');
    } else {
      this.errorMessage.set('');
    }
  }

  ngOnChanges(changes: SimpleChanges): void {

    if (changes['inputDati']) {
      const normalized = Array.isArray(this.inputDati) ? this.inputDati : [this.inputDati];

      this.labels = normalized.map(el => el.name);
      this.types = normalized.map(el => el.type);
      this.id = normalized.map(el => el.id)
      this.required = normalized.map(el => el.required)
      this.labels.forEach(label => {
        if (!(label in this.formData)) {
          this.formData[label] = '';
        }
      });

      this.formDataChanged.emit(this.formData);

      this.id.forEach(idCampo => {this.inputCompilato.emit({
        id: idCampo, valido: false});
      });
    }
  }

  onInputChange(label: string, value: string, idCampo: string) {
    this.formData[label] = value;
    this.formDataChanged.emit(this.formData);

    const valido = String(value ?? '').trim() !== '';
    this.inputCompilato.emit({ id: idCampo, valido})
  }

  hide = signal(true);
  clickEvent(event: MouseEvent) {
    this.hide.set(!this.hide());
    event.stopPropagation();
  }

  getIndexes(n: number): number[] {
    return Array.from({ length: n }, (_, i) => i);
  }
}