import type { Services } from './interfaces';
import { RealSessionService } from './real-session';
import { RealDiagramService } from './real-diagram';
import { RealNoteService } from './real-note';
import { RealEventService } from './real-event';

export type { Services, ISessionService, IDiagramService, INoteService, IEventService } from './interfaces';

let servicesInstance: Services | null = null;

export function getServices(): Services {
  if (!servicesInstance) {
    servicesInstance = {
      session: new RealSessionService(),
      diagram: new RealDiagramService(),
      note: new RealNoteService(),
      event: new RealEventService(),
    };
  }
  return servicesInstance;
}

export function setServices(services: Services): void {
  servicesInstance = services;
}

export function resetServices(): void {
  servicesInstance = null;
}

export {
  RealSessionService,
  RealDiagramService,
  RealNoteService,
  RealEventService,
};
