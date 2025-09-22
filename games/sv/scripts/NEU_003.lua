-- NEU_003 is "Insightful Scholar"
-- Its effect is "Fanfare: Draw a card."

function on_fanfare(self, game_state)
  -- 'api' is the Python ScriptAPI object that we injected.
  -- 'self' is the Python Card object for this card.
  -- 'self.owner' is a property we will add to the card when it's in a zone.
  
  -- This line calls the Python api.draw_card() method.
  api.draw_card(self.owner, 1)
end