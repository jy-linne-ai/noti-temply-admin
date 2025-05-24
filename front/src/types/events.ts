export type EntityType = 'layout' | 'part' | 'template';

export type EventType = 
  | 'created'
  | 'updated'
  | 'deleted'
  | 'previewed'
  | 'published'
  | 'archived';

export interface Event {
  id: string;
  type: EventType;
  entityType: EntityType;
  entityId: string;
  timestamp: string;
  userId: string;
  metadata: {
    [key: string]: any;
  };
}

export interface EventSubscription {
  unsubscribe: () => void;
}

export type EventHandler = (event: Event) => void; 