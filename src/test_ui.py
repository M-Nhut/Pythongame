from ui import GameUI, DummyShop

shop = DummyShop()
ui = GameUI(shop_client=shop, size=(800,380))
ui.run()
