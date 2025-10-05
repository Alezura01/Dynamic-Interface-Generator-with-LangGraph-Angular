import { Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { DynamicResponseComponent } from './dynamic-response/dynamic-response.component';

export const appRoutes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'dynamic-response', component: DynamicResponseComponent },
];
