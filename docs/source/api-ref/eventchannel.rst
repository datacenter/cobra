EventChannel Module
===================
.. module:: eventchannel

******************************************
Using Cobra to receive event notifications
******************************************

The following section describes how to use Cobra to receive 
notifications of events that occur on APIC, including changes to 
classes, individual objects or a combination of both.


Prerequisites for Event Notification
------------------------------------

The cobra.eventchannel package must be imported and available

Example::

    import cobra.eventchannel

A standard directory object using a LoginSession must first be 
established, before you can begin to receive events.
.. note:: As of the time of writing, CertSession support for 
EventChannels in Cobra is unavailable due to CSCur12715


Instantiating an EventChannel
-----------------------------

A cobra.eventchannel.EventChannel object is used for subscribing to 
events and receiving notifications from the event channel. The 
instantiation references the directory object.

Example::

    ec = cobra.eventchannel.EventChannel(moDir)

Subscribing to Events
---------------------

After an EventChannel object has been created, you can begin to 
subscribe to events on that EventChannel, using the existing ClassQuery
and DnQuery objects. For example, to subscribe to all events that occur
on a fvTenant object:

Example::

    import cobra.mit.request
    
    tenantQuery = cobra.mit.request.ClassQuery('fvTenant')
    subscription = ec.subscribe(tenantQuery)
    print 'Subscription ID is {0}'.format(subscription.subid)

Refreshing Subscriptions
------------------------

By default, a subscription must be refreshed every 60 seconds. If you
wish to unsubscribe to an event, the supported mechanism for doing this
is to simply allow the subscription to lapse. If you wish to refresh a
subscription, you can use the refresh() method before the 60 seconds has
expired.

Example::

    subscription.refresh()

Receiving Events from the EventChannel
--------------------------------------

Events can be read from the EventChannel using the getEvents() method.
This method will return an array of Mo objects, containing the changes
to the object. getEvents() is a blocking call, and will return once an
event has been received on the websocket or after the timeout value
defined by socket (getdefaulttimeout()).

Example::

    events = ec.getEvents()
    for moevent in events:
    	print 'Event:      : {}'.format(moevent.moEventType)
    	print 'Dn          : {}'.format(moevent.dn)
    	print 'Class name  : {}'.format(moevent.moClassName)
    
    	if not moevent.moEventType == 'MoDelete':
    		print 'Changes:''
    		print moevent.changes


.. autoclass:: cobra.eventchannel.EventChannel
   :members:
   :special-members:
   :exclude-members: __weakref__

.. autoclass:: cobra.eventchannel.MoEvent
   :members:
   :special-members:
   :exclude-members: __weakref__

.. autoclass:: cobra.eventchannel.Subscription
   :members:
   :special-members:
   :exclude-members: __weakref__

