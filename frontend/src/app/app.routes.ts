import { Routes } from '@angular/router';
import { Planner } from './pages/planner/planner';
import { TeamManagement } from './pages/team/team';

export const routes: Routes = [
  { path: '', component: Planner, title: 'Shift Planner' },
  { path: 'team', component: TeamManagement, title: 'Team Management' },
  { path: '**', redirectTo: '' },
];
