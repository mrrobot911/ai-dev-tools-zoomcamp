import type { Services } from './interfaces';
import { MockSessionService } from './mock-session';
import { MockDiagramService } from './mock-diagram';
import { MockNoteService } from './mock-note';
import { MockEventService } from './mock-event';

export type { Services, ISessionService, IDiagramService, INoteService, IEventService } from './interfaces';

let servicesInstance: Services | null = null;

export function getServices(): Services {
  if (!servicesInstance) {
    servicesInstance = {
      session: new MockSessionService(),
      diagram: new MockDiagramService(),
      note: new MockNoteService(),
      event: new MockEventService(),
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
  MockSessionService,
  MockDiagramService,
  MockNoteService,
  MockEventService,
};
